#
# MIT License
#
# Copyright (c) 2020 Pablo Rodriguez Nava, @pablintino
#
#  Permission is hereby granted, free of charge, to any person obtaining a copy
#  of this software and associated documentation files (the "Software"), to deal
#  in the Software without restriction, including without limitation the rights
#  to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
#  copies of the Software, and to permit persons to whom the Software is
#  furnished to do so, subject to the following conditions:
#
#  The above copyright notice and this permission notice shall be included in all
#  copies or substantial portions of the Software.
#
#  THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
#  IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
#  FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
#  AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
#  LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
#  OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
#  SOFTWARE.
#


import binascii
import dataclasses
import logging
import os.path
import pathlib
import re
import shutil
import typing

import filelock
from black import sanitized_lines
from fastapi import BackgroundTasks
from sqlalchemy import select, update, func, alias
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

import edaparts.utils.models_parser
from edaparts.app.config import Config
from edaparts.models import FootprintReference, LibraryReference
from edaparts.models.internal.internal_models import CadType, StorableTask
from edaparts.models.internal.internal_models import (
    StorableLibraryResourceType,
    StorageStatus,
    StorableObjectRequest,
    StorableObjectDataUpdateRequest,
)
from edaparts.services import database
from edaparts.services.exceptions import ApiError
from edaparts.services.exceptions import (
    ResourceAlreadyExistsApiError,
    ResourceNotFoundApiError,
    InvalidFootprintApiError,
    InvalidSymbolApiError,
    InvalidStorableTypeError,
)
from edaparts.utils.files import hash_sha256
from edaparts.utils.helpers import BraceMessage as __l

__logger = logging.getLogger(__name__)

__STORABLE_DIR_PATH_FOOTPRINTS = "footprints"
__STORABLE_DIR_PATH_SYMBOLS = "symbols"
__storable_base_dirs: dict[CadType, dict[StorableLibraryResourceType, pathlib.Path]] = {
    CadType.KICAD: {
        StorableLibraryResourceType.FOOTPRINT: pathlib.Path(
            Config.MODELS_BASE_DIR
        ).joinpath(__STORABLE_DIR_PATH_FOOTPRINTS, str(CadType.KICAD.value)),
        StorableLibraryResourceType.SYMBOL: pathlib.Path(
            Config.MODELS_BASE_DIR
        ).joinpath(__STORABLE_DIR_PATH_SYMBOLS, str(CadType.KICAD.value)),
    },
    CadType.ALTIUM: {
        StorableLibraryResourceType.FOOTPRINT: pathlib.Path(
            Config.MODELS_BASE_DIR
        ).joinpath(__STORABLE_DIR_PATH_FOOTPRINTS, str(CadType.ALTIUM.value)),
        StorableLibraryResourceType.SYMBOL: pathlib.Path(
            Config.MODELS_BASE_DIR
        ).joinpath(__STORABLE_DIR_PATH_SYMBOLS, str(CadType.ALTIUM.value)),
    },
}


def __validate_input_path(
    path: str, cad_type: CadType, file_type: StorableLibraryResourceType
):
    extensions_matrix = {
        cad_type.KICAD: {
            StorableLibraryResourceType.FOOTPRINT: "kicad_mod",
            StorableLibraryResourceType.SYMBOL: "kicad_sym",
        },
        cad_type.ALTIUM: {
            StorableLibraryResourceType.FOOTPRINT: "pcblib",
            StorableLibraryResourceType.SYMBOL: "schlib",
        },
    }

    if os.path.isabs(path):
        raise ApiError(f"the given path {path} must be relative", http_code=400)

    if path.lower().startswith(
        (__STORABLE_DIR_PATH_FOOTPRINTS, __STORABLE_DIR_PATH_SYMBOLS)
    ):
        prefix = path.split(os.path.sep)
        raise ApiError(
            f"the given path {path} must not start by the reserved prefix: {prefix[0]}",
            http_code=400,
        )

    if (
        cad_type.KICAD
        and file_type == StorableLibraryResourceType.FOOTPRINT
        and not os.path.dirname(path).endswith(".pretty")
    ):
        raise ApiError(
            f"KiCAD footprint files must be stored in a directory suffixed with `.pretty`",
            http_code=400,
        )
    expected_extension = extensions_matrix[cad_type][file_type]
    if not path.lower().endswith(f".{expected_extension}"):
        raise ApiError(
            f"the given path {path} must end with .{expected_extension}", http_code=400
        )


async def __validate_kicad_footprint_duplication(
    db: AsyncSession, path: str, reference: str, model_id: int = None
):
    parent_dir = os.path.dirname(path)
    query = select(FootprintReference).filter(
        FootprintReference.path.startswith(parent_dir),
        FootprintReference.cad_type == CadType.KICAD,
        FootprintReference.reference == reference,
    )
    if model_id is not None:
        query = query.filter(FootprintReference.id != model_id)
    existing_footprint = (await db.scalars(query)).first()
    if existing_footprint:
        raise ResourceAlreadyExistsApiError(
            f"the given footprint duplicated the already existing one",
            conflicting_id=existing_footprint.id,
        )


def __validate_storable_type(storable_type: StorableLibraryResourceType):
    if storable_type not in (
        StorableLibraryResourceType.FOOTPRINT,
        StorableLibraryResourceType.SYMBOL,
    ):
        raise InvalidStorableTypeError(
            __l(
                "The given storable type was not expected [storable_type={0}]",
                storable_type.value,
            )
        )


def __get_error_for_type(storable_type):
    __validate_storable_type(storable_type)
    return (
        InvalidFootprintApiError
        if storable_type == StorableLibraryResourceType.FOOTPRINT
        else InvalidSymbolApiError
    )


def __get_model_for_storable_type(
    storable_type,
) -> typing.Type[FootprintReference | LibraryReference]:
    __validate_storable_type(storable_type)
    return (
        FootprintReference
        if storable_type == StorableLibraryResourceType.FOOTPRINT
        else LibraryReference
    )


def __get_library(
    file: pathlib.Path, cad_type: CadType, expected_type: StorableLibraryResourceType
):
    try:
        # Parse the given data
        lib = edaparts.utils.models_parser.parse_file(file, cad_type)
        # Be sure that the encoded data is of the expected type
        if expected_type != lib.library_type:
            raise __get_error_for_type(expected_type)(
                "The given library is not of the expected type. {expected_type="
                + str(expected_type.value)
                + ", file_type="
                + str(lib.library_type.value)
                + "}"
            )
        return lib
    except IOError as err:
        raise __get_error_for_type(expected_type)(
            f"The given Altium file is corrupt",
            err.args[0] if len(err.args) > 0 else None,
        )


async def update_object_data(
    db: AsyncSession,
    background_tasks: BackgroundTasks,
    storable_request: StorableObjectDataUpdateRequest,
):
    # For the shake of simplicity do not allow to change the path
    # If the path can be changed we should manage that the change is valid for
    # all the references to the same path, and update all of them to point to that path

    model = await db.get(
        __get_model_for_storable_type(storable_request.file_type),
        storable_request.model_id,
    )
    if not model:
        raise ResourceNotFoundApiError(
            "Storable object not found", missing_id=storable_request.model_id
        )

    # Skip if the model reference and file are identical
    target_file = __get_target_object_path(
        model.cad_type, storable_request.file_type, model.path
    )
    if (
        model.storage_status == StorageStatus.STORED
        and (
            storable_request.reference is None
            or model.reference == storable_request.reference
        )
        and target_file.exists()
        and hash_sha256(target_file) == hash_sha256(storable_request.filename)
    ):
        __logger.debug(
            "Given new storable object data has the same content and reference as the current one. Skipping..."
        )
        return model

    lib = __get_library(
        storable_request.filename, model.cad_type, storable_request.file_type
    )

    # If a reference was provided it should be a valid one
    if storable_request.reference and not lib.is_present(storable_request.reference):
        raise __get_error_for_type(storable_request.file_type)(
            "The provided reference was not found in the given library"
        )
    elif (
        storable_request.reference is None
        and model.reference
        and not lib.is_present(model.reference)
    ):
        raise __get_error_for_type(storable_request.file_type)(
            "no reference provided for the file update and the existing one is not present in the given library"
        )
    if storable_request.reference is not None:
        await __validate_storable_not_exists(
            db,
            model.path,
            storable_request.reference,
            storable_request.file_type,
            model.cad_type,
            model_id=model.id,
        )

    # Reset storage status
    model.storage_status = StorageStatus.NOT_STORED
    db.add(model)
    await db.commit()

    # Signal background process to store the storable object
    background_tasks.add_task(
        _object_store_task,
        StorableTask(
            model_id=model.id,
            filename=storable_request.filename,
            path=model.path,
            file_type=storable_request.file_type,
            cad_type=model.cad_type,
            # NOTICE: References are changed inside the task to ensure reference checks are done with the file lock
            reference=storable_request.reference or model.reference,
        ),
    )
    return model


async def create_storable_library_object(
    db: AsyncSession,
    background_tasks: BackgroundTasks,
    storable_request: StorableObjectRequest,
) -> FootprintReference | LibraryReference:
    __validate_storable_type(storable_request.file_type)
    __validate_input_path(
        storable_request.path, storable_request.cad_type, storable_request.file_type
    )

    # Parse storable object from encoded data and check its content
    lib = __get_library(
        storable_request.filename,
        storable_request.cad_type,
        storable_request.file_type,
    )

    # Verify that the body contains enough information
    if not storable_request.reference:
        # Try to obtain the reference from the library data
        if lib.count != 1:
            raise __get_error_for_type(storable_request.file_type)(
                "More than one part in the given library. Provide a reference"
            )

        storable_request = dataclasses.replace(
            storable_request, reference=lib.models[next(iter(lib.models.keys()))].name
        )

    # If check that the given reference exists
    if not lib.is_present(storable_request.reference):
        raise __get_error_for_type(storable_request.file_type)(
            "The given reference does not exist in the given library "
        )

    # If no description is provided try to populate it from library data
    if not storable_request.description:
        storable_request = dataclasses.replace(
            storable_request,
            description=lib.models[storable_request.reference].description,
        )

    __logger.debug(
        __l(
            "Creating a new storable object [file_type={0}, reference_name={1}, storable_path={2}, description={3}]",
            storable_request.file_type,
            storable_request.reference,
            storable_request.path,
            storable_request.description,
        )
    )

    await __validate_storable_not_exists(
        db,
        storable_request.path,
        storable_request.reference,
        storable_request.file_type,
        storable_request.cad_type,
    )

    # Create a model based on the storable object type
    model = __get_model_for_storable_type(storable_request.file_type)(
        path=storable_request.path,
        reference=storable_request.reference,
        # Ensure that storage status at creation time is set to NOT_STORED
        storage_status=StorageStatus.NOT_STORED,
        description=storable_request.description,
        cad_type=storable_request.cad_type,
        alias=__get_model_alias(storable_request),
    )

    db.add(model)
    await db.commit()
    __logger.debug(__l("Storable object created [id={0}]", model.id))

    # Signal background process to store the object
    background_tasks.add_task(
        _object_store_task,
        StorableTask(
            model_id=model.id,
            filename=storable_request.filename,
            path=model.path,
            file_type=storable_request.file_type,
            cad_type=model.cad_type,
            reference=model.reference,
        ),
    )

    return model


def __get_model_alias(storable_request: StorableObjectRequest) -> typing.Optional[str]:
    if storable_request.cad_type != CadType.KICAD:
        return None

    if storable_request.file_type == StorableLibraryResourceType.FOOTPRINT:
        lib_path_name = (
            os.path.basename(os.path.dirname(storable_request.path))
            .lower()
            .replace(".pretty", "")
        )
    else:
        lib_path_name = storable_request.path.lower().rsplit(".", maxsplit=1)[0]

    sanitized_name = re.sub("[^0-9a-z]+", "_", lib_path_name).strip("_").upper()
    return f"EDAPARTS_{sanitized_name}"


async def _object_store_task(storable_task: StorableTask):
    async with database.sessionmanager.session() as session:
        error = None
        await __store_file_set_state(
            session,
            storable_task.model_id,
            storable_task.file_type,
            StorageStatus.STORING,
        )
        try:
            target_file = __get_target_object_path(
                storable_task.cad_type, storable_task.file_type, storable_task.path
            )
            if not target_file.parent.exists():
                target_file.parent.mkdir(parents=True)

            await __store_file(session, storable_task, target_file)
        except SQLAlchemyError as err:
            error = err
            __logger.critical(
                __l(
                    "SQLAlchemyError error persisting [model_id={0}, storable_task={1}]",
                    storable_task.model_id,
                    storable_task,
                ),
                exc_info=True,
            )
        except ApiError as err:
            # Internal error that doesn't mean the task is failing, the payload may be wrong,
            # and we should pass the message to the user
            error = err
            __logger.debug(err.msg)
        finally:
            # Remove the temporal file
            os.remove(storable_task.filename)

        if error:
            # Update the state to signal something failed
            await __store_file_set_state(
                session,
                storable_task.model_id,
                storable_task.file_type,
                StorageStatus.STORAGE_FAILED,
                error_description=str(error),
            )


def __get_target_object_path(
    cad_type: CadType, file_type: StorableLibraryResourceType, path: str
) -> pathlib.Path:
    return __storable_base_dirs[cad_type][file_type].joinpath(path)


async def __store_file(
    session: AsyncSession,
    storable_task: StorableTask,
    target_file: pathlib.Path,
):
    with filelock.FileLock(target_file.with_suffix(".lock"), timeout=30):
        await __store_file_validate(session, storable_task)

        model_type = __get_model_for_storable_type(storable_task.file_type)
        current_reference = (await session.scalars(select(model_type.reference))).one()
        if current_reference != storable_task.reference:
            await __validate_storable_not_exists(
                session,
                storable_task.path,
                storable_task.reference,
                storable_task.file_type,
                storable_task.cad_type,
                model_id=storable_task.model_id,
            )
            await session.execute(
                update(model_type)
                .where(model_type.id == storable_task.model_id)
                .values(reference=storable_task.reference)
            )

        # Checks done, copy the content
        shutil.copy(storable_task.filename, target_file)

        # Update the state
        await __store_file_set_state(
            session,
            storable_task.model_id,
            storable_task.file_type,
            StorageStatus.STORED,
        )


async def __store_file_validate(session: AsyncSession, storable_task: StorableTask):
    if (
        storable_task.cad_type == CadType.KICAD
        and storable_task.file_type == StorableLibraryResourceType.FOOTPRINT
    ):
        # KiCAD footprints do not have a single file lib, each file contains one single footprint.
        # As we warranty at input time that each file has the specified reference and that
        # there is not duplication in the references the regular check to multi-model files do not
        # make sense
        return

    # Parse the library again with the lock to avoid race conditions
    library = __get_library(
        storable_task.filename, storable_task.cad_type, storable_task.file_type
    )
    references_list = (await __get_stored_references_for_id(session, storable_task)) + [
        storable_task.reference
    ]
    # The reference in the task may be the existing one if no changes to it are needed
    # or the new one if we need to update it. In any case, both needs to be present.
    for reference in references_list:
        if not library.is_present(reference):
            raise ApiError(
                f"update to {storable_task.filename} will remove an existing reference {reference}"
            )


async def __get_stored_references_for_id(
    db: AsyncSession, storable_task: StorableTask
) -> [str]:
    # Get all stored references but the one we are creating
    model_type = __get_model_for_storable_type(storable_task.file_type)
    return list(
        (
            await db.scalars(
                select(model_type.reference).filter(
                    model_type.path == storable_task.path,
                    model_type.cad_type == storable_task.cad_type,
                    model_type.id != storable_task.model_id,
                    model_type.storage_status == StorageStatus.STORED,
                )
            )
        ).all()
    )


async def __validate_storable_not_exists(
    db: AsyncSession,
    storable_path: str,
    reference_name: str,
    file_type: StorableLibraryResourceType,
    cad_type: CadType,
    model_id: int = None,
):
    if file_type == StorableLibraryResourceType.FOOTPRINT and cad_type == CadType.KICAD:
        await __validate_kicad_footprint_duplication(
            db, storable_path, reference_name, model_id=model_id
        )
        # Do not do the regular checks as in KiCAD footprints each file only has a single footprint
        return

    model_type = __get_model_for_storable_type(file_type)
    query = select(model_type).filter(
        model_type.path == storable_path, model_type.reference == reference_name
    )
    query = query.filter(model_type.id != model_id) if model_id is not None else query
    exists_model = (await db.scalars(query)).first()
    if exists_model:
        raise ResourceAlreadyExistsApiError(
            "Cannot create the requested storable object cause it already exists",
            conflicting_id=exists_model.id,
        )


async def __store_file_set_state(
    session: AsyncSession,
    model_id: int,
    file_type: StorableLibraryResourceType,
    status: StorageStatus,
    error_description: str = None,
):
    model_type = __get_model_for_storable_type(file_type)
    try:
        await session.execute(
            update(model_type)
            .where(model_type.id == model_id)
            .values(storage_status=status, storage_error=error_description)
        )
        await session.commit()
    except SQLAlchemyError as err:
        __logger.error(
            __l(
                "unexpected error saving symbol reference state [model_id={0}, file_type={1}, status={2}, error_description={3}, err={4}]",
                model_id,
                file_type,
                status,
                error_description,
                str(err),
            )
        )


async def get_storable_model(
    session: AsyncSession, storable_type: StorableLibraryResourceType, model_id: int
) -> FootprintReference | LibraryReference:
    __logger.debug(
        __l(
            "Retrieving a storable object [storable_type={0}, model_id={1}]",
            storable_type.value,
            model_id,
        )
    )
    model = await session.get(__get_model_for_storable_type(storable_type), model_id)
    if not model:
        raise ResourceNotFoundApiError("Storable object not found", missing_id=model_id)

    return model


async def get_storable_objects(
    db: AsyncSession, storable_type: StorableLibraryResourceType, page_number, page_size
) -> typing.Tuple[list[FootprintReference | LibraryReference], int]:
    __logger.debug(
        __l(
            "Querying all storable objects [storable_type={0}, page_number={1}, page_size={2}]",
            storable_type.value,
            page_number,
            page_size,
        )
    )

    model_type = __get_model_for_storable_type(storable_type)
    # todo: extract to common place
    _count_column_name = "__private_edaparts_get_category_items_row_count"
    new_query = select(model_type).add_columns(
        func.count().over().label(_count_column_name)
    )
    rows_result = (await db.execute(new_query)).fetchall()
    results = []
    total = 0
    for index in range(len(rows_result)):
        row_data = rows_result[index]
        if index == 0:
            total = row_data[1]
        results.append(row_data[0])
    return results, total
