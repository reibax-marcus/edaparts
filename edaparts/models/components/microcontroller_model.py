#
# MIT License
#
# Copyright (c) 2024 Pablo Rodriguez Nava, @pablintino
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


from sqlalchemy import Column, String, ForeignKey
from edaparts.models.components.component_model import ComponentModel


class MicrocontrollerModel(ComponentModel):
    __tablename__ = "comp_microcontroller"
    __id_prefix__ = "MCRO"

    # Primary key
    id = Column(ForeignKey("component.id"), primary_key=True)

    # Specific properties of a resistor
    core = Column(String(50))
    core_size = Column(String(30))
    speed = Column(String(30))
    flash_size = Column(String(30))
    ram_size = Column(String(30))
    peripherals = Column(String(250))
    connectivity = Column(String(250))
    voltage_supply = Column(String(50))

    # Tells the ORM the type of a specific component by the distinguish column
    __mapper_args__ = {
        "polymorphic_identity": __tablename__,
    }
