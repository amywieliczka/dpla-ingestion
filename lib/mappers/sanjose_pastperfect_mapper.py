from dplaingestion.mappers.pastperfect_xml_mapper import PastPerfectXMLMapper

COUCH_ID_BUILDER = lambda src, lname: "--".join((src, lname))


class SanJose_PastPerfectMapper(PastPerfectXMLMapper):
    def __init__(self, provider_data, key_prefix=None):
        super(SanJose_PastPerfectMapper, self).__init__(
            provider_data, key_prefix)
        self.metadata = self.provider_data.get('metadata', self.provider_data)

    # Don't create sourceResource, isShownBy or isShownAt for
    # thumbnail-less objects, so they do not get passed through to SOLR
    def map_source_resource(self):
        if 'thumbnail' in self.metadata:
            super(SanJose_PastPerfectMapper, self).map_source_resource()

    def map_is_shown_at(self, index=None):
        '''Set is_shownBy as well'''
        if 'thumbnail' in self.metadata:
            self.mapped_data.update({"isShownAt": self.metadata.get('url')[0]})
            if '.tif' in self.metadata.get('thumbnail')[0]:
                jpg_url = self.metadata.get('thumbnail')[0].replace(
                        ".tif", ".jpg")
                self.mapped_data.update({"isShownBy": jpg_url})
            else:
                self.mapped_data.update({
                    "isShownBy":
                    self.metadata.get('thumbnail')[0]
                })
