""" Views for OAI-PMH List Records API """


from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import render
from django.utils.timezone import UTC, make_aware
from django.utils import timezone

from oaipmh.datestamp import tolerant_datestamp_to_datetime
from oaipmh.error import DatestampError

from datetime import datetime

from .models import OaiFormat, OaiRecord, OaiSet
from .utils import to_kv_pairs, OaiRequestError
from .settings import (
  OAI_BASE_URL, OAI_ENDPOINT_NAME,
  REPOSITORY_NAME, ADMIN_EMAIL
)
from .resumption import handle_list_query, resume_request


def format_error(error_code, error_message, context, request):
    context['error_code'] = error_code
    context['error_message'] = error_message
    return render(request, 'oai/error.xml', context, content_type='text/xml')


def endpoint(request):
    verb = request.GET.get('verb')
    this_url = 'http'
    if request.is_secure():
        this_url = this_url+'s'
    this_url = this_url+'://' + request.get_host() + request.get_full_path()
    timestamp = datetime.utcnow()
    timestamp = timestamp.replace(microsecond=0)
    context = {'this_url': this_url,
               'timestamp': timestamp.isoformat() + 'Z'}
    if not verb:
        return format_error('badVerb', 'No verb specified!', context, request)

    params = request.GET
    context['params'] = to_kv_pairs(params)

    try:
        if verb == 'Identify':
            return identify(request, context)
        elif verb == 'GetRecord':
            return get_record(request, context)
        elif verb == 'ListRecords' or verb == 'ListIdentifiers' or verb == 'ListSets':
            return list_something(request, context, verb)
        elif verb == 'ListMetadataFormats':
            return list_metadata_formats(request, context)
        else:
            raise OaiRequestError(
                'badVerb', 'Verb "' + verb + '" is not implemented.')
    except OaiRequestError as e:
        return format_error(e.code, e.reason, context, request)


def identify(request, context):
    context['baseURL'] = OAI_BASE_URL + '/' + OAI_ENDPOINT_NAME
    context['repoName'] = REPOSITORY_NAME
    context['adminEmail'] = ADMIN_EMAIL
    earliest = OaiRecord.objects.order_by('timestamp')[0]
    if earliest:
        context['earliestDatestamp'] = earliest.timestamp
    else:
        context['earliestDatestamp'] = timezone.now()
    return render(request, 'oai/identify.xml', context, content_type='text/xml')


def get_record(request, context):
    format_name = request.GET.get('metadataPrefix')
    try:
        oai_format = OaiFormat.objects.get(name=format_name)
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
    return render(request, 'oai/GetRecord.xml', context, content_type='text/xml')


def list_something(request, context, verb):
    if 'resumptionToken' in request.GET:
        return resume_request(context, request, verb, request.GET.get('resumptionToken'))
    query_parameters = dict()
    if verb == 'ListRecords' or verb == 'ListIdentifiers':
        query_parameters = get_list_query(context, request)
    return handle_list_query(request, context, verb, query_parameters)


def list_metadata_formats(request, context):
    matches = OaiFormat.objects.all()
    if 'identifier' in request.GET:
        identifier = request.GET.get('identifier')
        records = OaiRecord.objects.filter(identifier=identifier)
        if records.count() == 0:
            raise OaiRequestError(
                'badArgument', 'This identifier "' + identifier + '" does not exist.')
        context['records'] = records
        return render(request, 'oai/ListFormatsByIdentifier.xml', context, content_type='text/xml')
    else:
        context['matches'] = matches
        return render(request, 'oai/ListMetadataFormats.xml', context, content_type='text/xml')


def get_list_query(context, request):
    """
    Returns the query dictionary corresponding to the request
    Raises OaiRequestError if anything goes wrong
    """
    query_parameters = dict()

    # Both POST and GET arguments *must* be supported according to the standard
    # In this implementation, POST arguments are prioritary.
    getParams = dict(request.GET.dict().items() + request.POST.dict().items())

    # metadataPrefix
    metadataPrefix = getParams.pop('metadataPrefix', None)
    if not metadataPrefix:
        raise OaiRequestError(
            'badArgument', 'The metadataPrefix argument is required.')
    try:
        oai_format = OaiFormat.objects.get(name=metadataPrefix)
    except ObjectDoesNotExist:
        raise OaiRequestError(
            'badArgument', 'The metadata format "' + metadataPrefix + '" does not exist.')
    query_parameters['format'] = oai_format

    # set
    set_by_param = getParams.pop('set', None)
    if set_by_param:
        matching_set = OaiSet.by_representation(set_by_param)
        if not matching_set:
            raise OaiRequestError(
                'badArgument', 'The set "' + set_by_param + '" does not exist.')
        query_parameters['sets'] = matching_set

    # from
    from_ = getParams.pop('from', None)
    if from_:
        try:
            from_ = tolerant_datestamp_to_datetime(from_)
        except DatestampError:
            raise OaiRequestError('badArgument',
                                  'The parameter "from" expects a valid date, not "' + from_ + "'.")
        query_parameters['timestamp__gte'] = make_aware(from_, UTC())

    # until
    until = getParams.pop('until', None)
    if until:
        try:
            until = tolerant_datestamp_to_datetime(until)
        except DatestampError:
            raise OaiRequestError('badArgument',
                                  'The parameter "until" expects a valid date, not "' + until + "'.")
        query_parameters['timestamp__lte'] = make_aware(until, UTC())

    # Check that from <= until
    if from_ and until and from_ > until:
        raise OaiRequestError(
            'badArgument', '"from" should not be after "until".')

    # Check that there are no other arguments
    getParams.pop('verb', None)
    for key in getParams:
        raise OaiRequestError(
            'badArgument', 'The argument "' + key + '" is illegal.')

    return query_parameters
