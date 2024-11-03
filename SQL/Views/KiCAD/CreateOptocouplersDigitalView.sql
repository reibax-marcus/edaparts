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

create or replace view "KiCad Optocouplers Digital" as
select c.mpn                                  "Part Number",
       c.value                                "Value",
       c.manufacturer                         "Manufacturer",
       c.created_on                           "Created On",
       c.updated_on                           "Updated On",
       c.package                              "Package",
       c.description                          "Description",
       c.comment_altium                       "Comment",
       c.operating_temperature_min            "Minimum Operating Temperature",
       c.operating_temperature_max            "Maximum Operating Temperature",
       CONCAT(l.alias, ':', l.reference)      "Symbol",
       CONCAT_WS(';', ftp1, ftp2, ftp3, ftp4) "Footprints",
       o.voltage_isolation                    "Isolation Voltage",
       o.voltage_saturation_max               "Maximum Saturation Voltage",
       o.current_transfer_ratio_max           "Maximum Current Transfer Ratio",
       o.current_transfer_ratio_min           "Minimum Current Transfer Ratio",
       o.voltage_forward_typical              "Typical Forward Voltage",
       o.voltage_output_max                   "Maximum Output Voltage",
       o.number_of_channels                   "Number of Channels"
from crosstab('select c.id, ROW_NUMBER() OVER (ORDER BY c.id, f.id) seq, CONCAT(f.alias, '':'', f.reference)
    from optocoupler_digital o
             inner join component c
                        on o.id = c.id
             inner join component_footprint_asc cf
                        on c.id = cf.component_id
             inner join footprint_ref f
                        on cf.footprint_ref_id = f.id
             where f.cad_type = ''KICAD''::cadtype'
     ) as ct(cid int, ftp1 text, ftp2 text, ftp3 text, ftp4 text)
         right outer join component c on c.id = cid
         inner join optocoupler_digital o on o.id = c.id
         left outer join library_ref l on c.library_ref_id = l.id
where l.cad_type = 'KICAD'::cadtype