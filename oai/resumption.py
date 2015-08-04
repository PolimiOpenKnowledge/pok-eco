# -*- encoding: utf-8 -*-
from __future__ import unicode_literals

from django.shortcuts import render
from django.utils.timezone import make_naive, UTC, make_aware

from .models import OaiRecord, OaiSet, ResumptionToken
from .settings import RESULTS_LIMIT
from .utils import OaiRequestError

def handle_list_query(request, context, queryType, parameters, offset=0):
    # TODO use offset
    if queryType == 'ListRecords' or queryType == 'ListIdentifiers':
        matches = OaiRecord.objects.filter(**parameters)
    elif queryType == 'ListSets':
        matches = OaiSet.objects.all()
    else:
        return OaiRequestError('badArgument', 'Illegal verb.')
    count = matches.count()
    # Should we create a resumption token?
    if count-offset > RESULTS_LIMIT:
        token = create_resumption_token(queryType, parameters, offset+RESULTS_LIMIT, count)
        context['token'] = token
    context['matches'] = matches[offset:(offset+RESULTS_LIMIT)]
    return render(request, 'oai/'+queryType+'.xml', context, content_type='application/xml')


def create_resumption_token(queryType, query_parameters, offset, total_count):
    token = ResumptionToken(queryType=queryType, offset=offset,
                            cursor=offset-RESULTS_LIMIT, total_count=total_count)
    if 'format' in query_parameters:
        token.metadataPrefix = query_parameters['format']
    if 'timestamp__gte' in query_parameters:
        token.fro = make_aware(query_parameters['timestamp__gte'], UTC())
    if 'timestamp__lte' in query_parameters:
        token.until = make_aware(query_parameters['timestamp__lte'], UTC())
    if 'sets' in query_parameters:
        token.set = query_parameters['sets']
    token.save()
    token.genkey()
    return token


def resume_request(context, request, queryType, key):
    token = ResumptionToken.objects.get(queryType=queryType, key=key)
    if not token:
        return OaiRequestError('badResumptionToken', 'This resumption token is invalid.')
    parameters = dict()
    parameters['format'] = token.metadataPrefix
    if token.set:
        parameters['sets'] = token.set
    if token.fro:
        parameters['timestamp__gte'] = make_naive(token.fro, UTC())
    if token.until:
        parameters['timestamp__lte'] = make_naive(token.until, UTC())
    return handle_list_query(request, context, queryType, parameters, token.offset)
