from django.conf import settings
from django.core.servers.basehttp import FileWrapper
from django.http import HttpResponse, HttpResponseServerError, Http404, HttpResponseBadRequest
from django.shortcuts import get_list_or_404, get_object_or_404, render_to_response, redirect
from aigapages.bib.models import Author, Publication
from os import path
from aigapages.bib.helpers import *


def view_all(request):
    publications = Publication.objects.filter(author__institute='Facultad de Informatica')
    return listing_response(publications, request.GET)

def view_author(request, author_id):
    author = get_object_or_404(Author, author_id=author_id, 
        institute='Facultad de Informatica')
    return listing_response(author.publications, request.GET)


def download_fulltext(request, pub_id):
    publication = get_object_or_404(Publication, pub_id = pub_id)
    attachment  = get_object_or_404(publication.attachments_set.all(), ismain=True)
    if attachment.isremote == "TRUE": 
        return redirect(attachment.location)
    else:
        filename = path.join(settings.ATTACHMENT_DIR, attachment.location)
        response = HttpResponse(FileWrapper(file(filename)), content_type=attachment.mime)
        response['Content-Disposition'] = ('attachment; filename=%s' % attachment.name)
        return response

def view_bibtex(request, pub_id):
    pub = get_object_or_404(Publication, pub_id = pub_id)
    fields = [
        ('title', pub.title),
        ('author', print_authors(pub.author_list())),
        ('editor', print_authors(pub.editor_list())),
        ('journal', pub.journal),
        ('series', pub.series),
        ('volume', pub.volume),
        ('number', pub.number),   
        ('booktitle', pub.booktitle),
        ('publisher', pub.publisher),
        ('pages', pub.pages),
        ('year', pub.year),
        ('month', pub.cleanmonth()),
        ('abstract', pub.abstract),
        ('address', pub.location),
        ('issn', pub.issn),
        ('isbn', pub.isbn),
        ('note', pub.note),  
    ]

    if pub.chapter and pub.chapter <> '0':
        fields += [('chapter', pub.chapter)]

    fields += parse_userfields(pub.userfields)
    
    context = {
        'type': pub.pub_type,
        'key': pub.bibtex_id,
        'fields': filter(lambda field: field[1], fields)
    }
    return render_to_response('publication.bib', context, mimetype='text/plain') 



# vim:set ts=4 sw=4 et:
