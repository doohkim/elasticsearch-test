import abc

import elasticsearch
from elasticsearch_dsl import Q, Search, Index
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.response import Response
from rest_framework.views import APIView

from productions.documents import ProductionDocument
from productions.serializers import ProductionSerializer
from users.documents import BizUserDocument, BizBrandDocument
from users.serializers import BizUserSerializer, BizBrandSerializer


class PaginatedElasticSearchAPIView(APIView, LimitOffsetPagination):
    serializer_class = None
    document_class = None

    @abc.abstractmethod
    def generate_q_expression(self, query):
        pass

    def get(self, request, query):
        try:
            q = self.generate_q_expression(query)
            search = self.document_class.search().query(q)
            response = search.execute()
            print(f'response    {response}')
            results = self.paginate_queryset(response, request, view=self)
            serializer = self.serializer_class(results, many=True)
            return Response(serializer.data)
        except Exception as e:
            return Response(e, status=500)


class SearchBizUserAPIView(PaginatedElasticSearchAPIView):
    serializer_class = BizUserSerializer
    document_class = BizUserDocument

    def generate_q_expression(self, query):
        return Q('bool',
                 should=[
                     Q('match', username=query),
                     Q('match', name=query),
                 ], minimum_should_match=1)


class SearchProductionAPIView(PaginatedElasticSearchAPIView):
    serializer_class = ProductionSerializer
    document_class = ProductionDocument

    def generate_q_expression(self, query):
        print(query)
        # minimum_should_match를 통해서 최소 몇개만 해당하면 되는지도 설정이 가능하다.
        return Q('bool',
                 should=[
                     Q('match_phrase_prefix', name=query),
                 ], minimum_should_match=1)

    def get(self, requests, query):
        q = self.generate_q_expression(query)
        search = self.document_class.search().query(q)
        response = search.execute()
        data_list = [product['_source'] for product in response.to_dict()['hits']['hits']]
        serializer = ProductionSerializer(data_list, many=True)
        return Response(serializer.data)


class SearchBizBrandAPIView(PaginatedElasticSearchAPIView):
    serializer_class = BizBrandSerializer
    document_class = BizBrandDocument

    def generate_q_expression(self, query):
        # print(query)
        # return Q('bool',
        #          should=[
        #              Q('match_phrase_prefix', name=query),
        #          ], minimum_should_match=1)
        es = elasticsearch.Elasticsearch('localhost:9200')
        s = Search(index='bizbrands', using=es)
        s = s.query(
            'multi_match',
            query=query,
            fuzziness='auto',
            fields=['name', 'business_type']
        )
        return s
    def get(self, requests, query):

        s = self.generate_q_expression(query)
        res = s.execute()
        res.to_dict()
    #     print(q)
    #     search = self.document_class.search().query(q)
    #     print(search)
    #     response = search.execute()
    #     print(response)
        data_list = [product['_source'] for product in res.to_dict()['hits']['hits']]
        print(data_list)
        serializer = BizBrandSerializer(data_list, many=True)
        return Response(serializer.data)
