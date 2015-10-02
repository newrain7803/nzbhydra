import json
from pprint import pprint
import re
import unittest
from freezegun import freeze_time
import responses
from nzbhydra.database import Provider

from nzbhydra.searchmodules.newznab import NewzNab
from nzbhydra.tests import mockbuilder
from nzbhydra.tests.db_prepare import set_and_drop
from nzbhydra.tests.providerTest import ProviderTestcase


class MyTestCase(ProviderTestcase):

    def setUp(self):    
        set_and_drop()    
        self.nzbsorg = Provider(module="newznab", name="NZBs.org", settings={"apikey": "apikeynzbsorg", "query_url": "http://127.0.0.1:5001/nzbsorg", "base_url": "http://127.0.0.1:5001/nzbsorg", "search_types": ["tv", "general", "movie"], "search_ids": ["imdbid", "tvdbid", "rid"]})
        self.nzbsorg.save()
        self.dognzb = Provider(module="newznab", name="DOGNzb", settings={"apikey": "apikeydognzb", "query_url": "http://127.0.0.1:5001/dognzb", "base_url": "http://127.0.0.1:5001/dognzb", "search_types": ["tv", "general"], "search_ids": ["tvdbid", "rid"]})
        self.dognzb.save()
    
    @freeze_time("2015-09-20 14:00:00", tz_offset=-4)
    def testParseJsonToNzbSearchResult(self):
        
        n = NewzNab(self.nzbsorg)
        
        #nzbsorg
        with open("mock/nzbsorg_q_avengers_3results.json") as f:
            entries = n.process_query_result(f.read(), "aquery")["entries"]
        self.assertEqual(3, len(entries))
        
        self.assertEqual(entries[0].title, "Avengers.Age.Of.Ultron.2015.FRENCH.720p.BluRay.x264-Goatlove")
        assert entries[0].size == 6719733587
        assert entries[0].guid == "9c9d30fa2767e05ffd387db52d318ad7"
        self.assertEqual(entries[0].age_days, 2)
        self.assertEqual(entries[0].epoch, 1442581037)
        self.assertEqual(entries[0].pubdate_utc, "2015-09-18T12:57:17+00:00")
        
        
        assert entries[1].title == "Avengers.Age.of.Ultron.2015.1080p.BluRay.x264.AC3.5.1-BUYMORE"
        assert entries[1].size == 4910931143
        assert entries[1].guid == "eb74f6c0bf2125c0b410936276ac38f0"
        
        assert entries[2].title == "Avengers.Age.of.Ultron.2015.1080p.BluRay.DTS.x264-CyTSuNee"
        assert entries[2].size == 15010196044
        assert entries[2].guid == "41b305ac99507f70ed6a10e45177065c"
        
        
        n = NewzNab(self.dognzb)
        #dognzb
        with open("mock/dognzb_q_avengers_3results.json") as f:
            entries = n.process_query_result(f.read(), "aquery")["entries"]
        pprint(entries)
        assert len(entries) == 3
        
        assert entries[0].title == "Avengers.Age.Of.Ultron.2015.FRENCH.720p.BluRay.x264-Goatlove"
        assert entries[0].size == 6718866639
        assert entries[0].guid == "c6214fe5ae317b36906f0507042ca889"
        
        assert entries[1].title == "Avengers.Age.Of.Ultron.2015.1080p.BluRay.Hevc.X265.DTS-SANTI"
        assert entries[1].size == 5674463318
        assert entries[1].guid == "0199594cb9af69efb663e761848a76c2"
        
        assert entries[2].title == "Avengers.Age.Of.Ultron.2015.Truefrench.720p.BluRay.x264-AVITECH"
        assert entries[2].size == 6340781948
        assert entries[2].guid == "ea1b68d2ff97a5f0528b3d22c73f11ad"
        
    
    def testNewznabSearchQueries(self):
        
        nzbsorg = NewzNab(self.nzbsorg)
        self.args.update({"query": "aquery"})
        queries = nzbsorg.get_search_urls(self.args)
        assert len(queries) == 1
        query = queries[0]
        assert "http://127.0.0.1:5001/nzbsorg" in query
        assert "apikey=apikeynzbsorg" in query
        assert "t=search" in query
        assert "q=aquery" in query
        assert "o=json" in query
        
        self.args.update({"query": None})
        queries = nzbsorg.get_showsearch_urls(self.args)
        assert len(queries) == 1
        query = queries[0]
        assert "http://127.0.0.1:5001/nzbsorg?" in query
        assert "apikey=apikeynzbsorg" in query
        assert "t=tvsearch" in query
        assert "o=json" in query
        
        self.args.update({"category": "All"})
        queries = nzbsorg.get_showsearch_urls(self.args)
        assert len(queries) == 1
        query = queries[0]
        assert "http://127.0.0.1:5001/nzbsorg?" in query
        assert "apikey=apikeynzbsorg" in query
        assert "t=tvsearch" in query
        assert "o=json" in query
        
        self.args.update({"rid": "8511"})
        queries = nzbsorg.get_showsearch_urls(self.args)
        assert len(queries) == 1
        query = queries[0]
        assert "http://127.0.0.1:5001/nzbsorg?" in query
        assert "apikey=apikeynzbsorg" in query
        assert "t=tvsearch" in query
        assert "rid=8511" in query
        assert "o=json" in query
        
        self.args.update({"rid": "8511", "season": "1"})
        queries = nzbsorg.get_showsearch_urls(self.args)
        assert len(queries) == 1
        query = queries[0]
        assert "http://127.0.0.1:5001/nzbsorg?" in query
        assert "apikey=apikeynzbsorg" in query
        assert "t=tvsearch" in query
        assert "rid=8511" in query
        assert "o=json" in query
        assert "season=1" in query
        
        self.args.update({"rid": "8511", "season": "1", "episode":"2"})
        queries = nzbsorg.get_showsearch_urls(self.args)
        assert len(queries) == 1
        query = queries[0]
        assert "http://127.0.0.1:5001/nzbsorg?" in query
        assert "apikey=apikeynzbsorg" in query
        assert "t=tvsearch" in query
        assert "rid=8511" in query
        assert "o=json" in query
        assert "season=1" in query
        assert "ep=2" in query
        
        self.args.update({"imdbid": "12345678"})
        queries = nzbsorg.get_moviesearch_urls(self.args)
        assert len(queries) == 1
        query = queries[0]
        assert "http://127.0.0.1:5001/nzbsorg?" in query
        assert "apikey=apikeynzbsorg" in query
        assert "t=movie" in query
        assert "imdbid=12345678" in query
        assert "o=json" in query
        
        self.args.update({"imdbid": "12345678", "category": "Movies"})
        queries = nzbsorg.get_moviesearch_urls(self.args)
        assert len(queries) == 1
        query = queries[0]
        assert "http://127.0.0.1:5001/nzbsorg?" in query
        assert "apikey=apikeynzbsorg" in query
        assert "t=movie" in query
        assert "imdbid=12345678" in query
        assert "o=json" in query
        assert "cat=2000" in query
        
        
    @responses.activate
    def testGetNfo(self):
        with open("mock/dognzb--id-b4ba74ecb5f5962e98ad3c40c271dcc8--t-getnfo.xml", encoding="latin-1") as f:
            xml = f.read()
            
            url_re = re.compile(r'.*')
            responses.add(responses.GET, url_re,
                          body=xml, status=200,
                          content_type='application/x-html')
            dog = NewzNab(self.dognzb)
            nfo = dog.get_nfo("b4ba74ecb5f5962e98ad3c40c271dcc8")
            assert "Road Hard" in nfo
            
    @responses.activate
    def testOffsetStuff(self):
        nzbsorg = NewzNab(self.nzbsorg)
        
        mockitem_nzbs = []
        for i in range(100):
            mockitem_nzbs.append(mockbuilder.buildNewznabItem("myId", "myTitle", "myGuid", "http://nzbs.org/myId.nzb", None, None, 12345, "NZBs.org", [2000, 2040]))
        mockresponse_nzbs1 = mockbuilder.buildNewznabResponse("NZBs.org", mockitem_nzbs, offset=0, total=200)
        
        mockitem_nzbs.clear()
        for i in range(100):
            mockitem_nzbs.append(mockbuilder.buildNewznabItem("myId", "myTitle", "myGuid", "http://nzbs.org/myId.nzb", None, None, 12345, "NZBs.org", [2000, 2040]))
        mockresponse_nzbs2 = mockbuilder.buildNewznabResponse("NZBs.org", mockitem_nzbs, offset=100, total=200)

        r = nzbsorg.process_query_result(json.dumps(mockresponse_nzbs1), "http://127.0.0.1:5001/nzbsorg/q=whatever&offset=0&limit=0")
        further_queries = r["queries"]
        self.assertEqual(1, len(further_queries))
        assert "offset=100" in further_queries[0]
        
        r = nzbsorg.process_query_result(json.dumps(mockresponse_nzbs2), "http://127.0.0.1:5001/nzbsorg/q=whatever&offset=0&limit=0")
        further_queries = r["queries"]
        self.assertEqual(0, len(further_queries))