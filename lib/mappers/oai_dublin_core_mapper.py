import requests
from dplaingestion.mappers.dublin_core_mapper import DublinCoreMapper
from dplaingestion.selector import exists, getprop


class OAIDublinCoreMapper(DublinCoreMapper):
    '''Dublin core mapper with a split on semicolons function.
    Many OAI feeds seem to do this.
    Override the particular fields that this holds for in their
    map_<field> function

    The map_is_shown_by & map_is_shown_at need to be created for each feed.
    '''
    def __init__(self, provider_data):
        super(OAIDublinCoreMapper, self).__init__(provider_data)

    def split_values(self, prop):
        new_values = []
        if exists(self.provider_data_source, prop):
            for value in filter(None, getprop(self.provider_data_source, prop)):
                new_values.extend([s.strip() for s in value.split(';')])
        return new_values

    def to_source_resource_with_split(self, provider_prop, srcRes_prop):
        '''Copy the provider_prop to the srcRes_prop & split on ; in
        data values'''
        values = self.split_values(provider_prop)
        self.update_source_resource({srcRes_prop: values})

    def source_resource_orig_list_to_prop_with_split(
            self,
            original_fields,
            srcRes_prop):
        '''for a list of fields in the providers original data, append the
        values into a single sourceResource field
        Split the values on ;
        '''
        values = []
        for field in original_fields:
            if exists(self.provider_data_source, field):
                split_src_value = self.split_values(field)
                values.extend(split_src_value)
        if values:
            self.update_source_resource({srcRes_prop: values})

# Copyright © 2016, Regents of the University of California
# All rights reserved.
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
# - Redistributions of source code must retain the above copyright notice,
#   this list of conditions and the following disclaimer.
# - Redistributions in binary form must reproduce the above copyright notice,
#   this list of conditions and the following disclaimer in the documentation
#   and/or other materials provided with the distribution.
# - Neither the name of the University of California nor the names of its
#   contributors may be used to endorse or promote products derived from this
#   software without specific prior written permission.
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
# ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER OR CONTRIBUTORS BE
# LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
# CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
# SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
# INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN
# CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
# ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
# POSSIBILITY OF SUCH DAMAGE.
