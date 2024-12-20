/**
 * MIT License
 *
 * Copyright (c) 2024 Pablo Rodriguez Nava, @pablintino
 *
 * Permission is hereby granted, free of charge, to any person obtaining a copy
 * of this software and associated documentation files (the "Software"), to deal
 * in the Software without restriction, including without limitation the rights
 * to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
 * copies of the Software, and to permit persons to whom the Software is
 * furnished to do so, subject to the following conditions:
 *
 * The above copyright notice and this permission notice shall be included in all
 * copies or substantial portions of the Software.
 *
 * THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
 * IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
 * FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
 * AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
 * LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
 * OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
 * SOFTWARE.
 *
 **/

create or replace view "Altium Triacs" as
select distinct on (c.id) c.mpn                       "Part Number",
                          c.value                     "Value",
                          c.manufacturer              "Manufacturer",
                          c.created_on                "Created On",
                          c.updated_on                "Updated On",
                          c.package                   "Package",
                          c.description               "Description",
                          c.comment_altium            "Comment",
                          c.operating_temperature_min "Minimum Operating Temperature",
                          c.operating_temperature_max "Maximum Operating Temperature",
                          l.path                      "Library Path",
                          l.reference                 "Library Ref",
                          (ftp1).path                 "Footprint Path",
                          (ftp2).path                 "Footprint Path 2",
                          (ftp3).path                 "Footprint Path 3",
                          (ftp4).path                 "Footprint Path 4",
                          (ftp1).reference            "Footprint Ref",
                          (ftp2).reference            "Footprint Ref 2",
                          (ftp3).reference            "Footprint Ref 3",
                          (ftp4).reference            "Footprint Ref 4",
                          t.power_max                 "Maximum Power",
                          t.vdrm                      "Vdrm",
                          t.current_rating            "Current Rating",
                          t.dl_dt                     "Rate Rise Off-State Voltage",
                          t.trigger_current           "Trigger Current",
                          t.latching_current          "Latching Current",
                          t.holding_current           "Holding Current",
                          t.gate_trigger_voltage      "Gate Trigger Voltage",
                          t.emitter_forward_current   "Emitter Forward Current",
                          t.emitter_forward_voltage   "Emitter Forward Voltage",
                          t.triac_type                "Triac Type"
from crosstab('select c.id, ROW_NUMBER() OVER (ORDER BY c.id, f.id) seq, f
    from comp_triac t
             inner join component c
                        on t.id = c.id
             inner join component_footprint_asc cf
                        on c.id = cf.component_id
             inner join footprint_ref f
                        on cf.footprint_ref_id = f.id
             where f.cad_type = ''ALTIUM''::cadtype'
     ) as ct(cid int, ftp1 footprint_ref, ftp2 footprint_ref, ftp3 footprint_ref, ftp4 footprint_ref)
         right outer join component c on c.id = cid
         inner join comp_triac t on t.id = c.id
         inner join component_library_asc cl on cl.component_id = c.id
         left outer join library_ref l on cl.library_ref_id = l.id
where l.cad_type = 'ALTIUM'::cadtype
order by c.id desc;
