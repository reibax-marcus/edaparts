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

from flask_restful import Resource
from dtos import components_models_dto_mappings
from dtos.schemas import schema_mapper
from rest_layer import handle_exception
from services import component_service
from services.exceptions import ApiError


class ComponentResource(Resource):

    def get(self, id):
        try:
            model = component_service.get_component(id)
            resulting_dto = components_models_dto_mappings.get_mapper_for_model(model).to_dto(model)
            return schema_mapper.get_schema_for_dto_class_name(resulting_dto.__class__.__name__)().dump(
                resulting_dto), 200
        except ApiError as error:
            return handle_exception(error)

    def delete(self, id):
        component_service.delete_component(id)
        return {}, 204