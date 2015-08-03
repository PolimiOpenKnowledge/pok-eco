""" Views for OAI-PMH List Records API """

from django.conf import settings
from django.utils.timezone import make_naive, UTC
from django.http import (
    QueryDict, HttpResponse,
    HttpResponseBadRequest, HttpResponseServerError
)
from datetime import datetime

from oai.models import *
from oai.utils import to_kv_pairs, OaiRequestError
from oai.settings import *
from oai.resumption import *


def formatError(errorCode, errorMessage, context, request):
    context['errorCode'] = errorCode
    context['errorMessage'] = errorMessage
    return render(request,'oai/error.xml', context, content_type='text/xml')


def endpoint(request):
    verb = request.GET.get('verb')
    thisUrl = 'http'
    if (request.is_secure()):
        thisUrl = thisUrl+'s'
    thisUrl = thisUrl+'://' + request.get_host() + request.get_full_path()
    timestamp = datetime.utcnow()
    timestamp = timestamp.replace(microsecond=0)
    context = {'thisUrl': thisUrl,
               'timestamp': timestamp.isoformat() + 'Z'}
    if not verb:
        return formatError('badVerb', 'No verb specified!', context, request)

    params = request.GET
    context['params'] = to_kv_pairs(params)

    try:
        if verb == 'Identify':
            return identify(request, context)
        elif verb == 'GetRecord':
            return getRecord(request, context)
        elif verb == 'ListRecords' or verb == 'ListIdentifiers' or verb == 'ListSets':
            return listSomething(request, context, verb)
        elif verb == 'ListMetadataFormats':
            return listMetadataFormats(request, context)
        else:
            raise OaiRequestError(
                'badVerb', 'Verb "' + verb + '" is not implemented.')
    except OaiRequestError as e:
        return formatError(e.code, e.reason, context, request)


def identify(request, context):
    context['baseURL'] = OAI_BASE_URL + '/' + OAI_ENDPOINT_NAME
    context['repoName'] = REPOSITORY_NAME
    context['adminEmail'] = ADMIN_EMAIL
    earliest = OaiRecord.objects.order_by('timestamp')[0]
    if earliest:
        context['earliestDatestamp'] = earliest.timestamp
    else:
        context['earliestDatestamp'] = timezone.now()
    return render(request,'oai/identify.xml', context, content_type='text/xml')


def getRecord(request, context):
    format_name = request.GET.get('metadataPrefix')
    try:
        format = OaiFormat.objects.get(name=format_name)
    except ObjectDoesNotExist:
        raise OaiRequestError(
            'badArgument', 'The metadata format "' + format_name + '" does not exist.')
    record_id = request.GET.get('identifier')
    try:
        record = OaiRecord.objects.get(identifier=record_id)
    except ObjectDoesNotExist:
        raise OaiRequestError(
            'badArgument', 'The record "' + record_id + '" does not exist.')
    context['record'] = record
    return render(request,'oai/GetRecord.xml', context, content_type='text/xml')


def listSomething(request, context, verb):
    if 'resumptionToken' in request.GET:
        return resumeRequest(context, request, verb, request.GET.get('resumptionToken'))
    queryParameters = dict()
    error = None
    if verb == 'ListRecords' or verb == 'ListIdentifiers':
        queryParameters = getListQuery(context, request)
    return handleListQuery(request, context, verb, queryParameters)


def listMetadataFormats(request, context):
    queryParameters = dict()
    matches = OaiFormat.objects.all()
    if 'identifier' in request.GET:
        id = request.GET.get('identifier')
        records = OaiRecord.objects.filter(identifier=id)
        if records.count() == 0:
            raise OaiRequestError(
                'badArgument', 'This identifier "' + id + '" does not exist.')
        context['records'] = records
        return render(request,'oai/ListFormatsByIdentifier.xml', context, content_type='text/xml')
    else:
        context['matches'] = matches
        return render(request,'oai/ListMetadataFormats.xml', context, content_type='text/xml')


def getListQuery(context, request):
    """
    Returns the query dictionary corresponding to the request
    Raises OaiRequestError if anything goes wrong
    """
    queryParameters = dict()

    # Both POST and GET arguments *must* be supported according to the standard
    # In this implementation, POST arguments are prioritary.
    getParams = dict(request.GET.dict().items() + request.POST.dict().items())

    # metadataPrefix
    metadataPrefix = getParams.pop('metadataPrefix', None)
    if not metadataPrefix:
        raise OaiRequestError(
            'badArgument', 'The metadataPrefix argument is required.')
    try:
        format = OaiFormat.objects.get(name=metadataPrefix)
    except ObjectDoesNotExist:
        raise OaiRequestError(
            'badArgument', 'The metadata format "' + metadataPrefix + '" does not exist.')
    queryParameters['format'] = format

    # set
    set = getParams.pop('set', None)
    if set:
        matchingSet = OaiSet.byRepresentation(set)
        if not matchingSet:
            raise OaiRequestError(
                'badArgument', 'The set "' + set + '" does not exist.')
        queryParameters['sets'] = matchingSet

    # from
    from_ = getParams.pop('from', None)
    if from_:
        try:
            from_ = tolerant_datestamp_to_datetime(from_)
        except DatestampError:
            raise OaiRequestError('badArgument',
                                  'The parameter "from" expects a valid date, not "' + from_ + "'.")
        queryParameters['timestamp__gte'] = make_aware(from_, UTC())

    # until
    until = getParams.pop('until', None)
    if until:
        try:
            until = tolerant_datestamp_to_datetime(until)
        except DatestampError:
            raise OaiRequestError('badArgument',
                                  'The parameter "until" expects a valid date, not "' + until + "'.")
        queryParameters['timestamp__lte'] = make_aware(until, UTC())

    # Check that from <= until
    if from_ and until and from_ > until:
        raise OaiRequestError(
            'badArgument', '"from" should not be after "until".')

    # Check that there are no other arguments
    getParams.pop('verb', None)
    for key in getParams:
        raise OaiRequestError(
            'badArgument', 'The argument "' + key + '" is illegal.')

    return queryParameters
