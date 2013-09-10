
(function($) {
    // Hang on in there. We have jQuery, 1.4.
    var BATCH_SIZE = 15;

    var ElasticSearch = function($form) {
        var search_urls = $form.data('server-urls'),
            index_name = $form.data('index-name');
        var empty_results = [],
            results = [];
        var previous_query = null,
            start_from = 0;

        var get_url = function() {
            var index = Math.floor(Math.random() * search_urls.length);
            return [search_urls[index], '/', index_name, '/_search'].join('');
        };

        var build_query = function(original) {
            var queries = [{
                    query_string : {
                        query: original.term,
                        default_operator: "AND",
                        fields: [
                            "title^3",
                            "contributors^2",
                            "subject^2",
                            "description",
                            "content"
                        ]
                    }
                }],
                query,
                filter,
                sort = {};
            // Sorting options.
            if (original.sort == 'created' || original.sort == 'modified') {
                sort[original.sort] = 'desc';
            } else if (original.sort == 'title') {
                sort = "sortableTitle";
            } else {
                sort = "_score";
            };
            // Other criterias
            if (original.contributors) {
                queries.push({match: {contributors: original.contributors}});
            };
            if (original.created) {
                queries.push({range: {created: {from: original.created}}});
            };
            if (original.published_year) {
                var pub_year = original.published_year;
                if (pub_year.match(/^\d{4}$/)) {
                    var range_op = original.published_before ? 'lt' : 'gt';
                    var pub_query = {range : {publishedYear : {}}};
                    pub_query.range.publishedYear[range_op] = pub_year;
                    queries.push(pub_query);
                }
            };
            if (original.url) {
                queries.push({prefix: {url: original.url}});
            };
            if (original.subject && original.subject.length) {
                var subjects = [], i;

                for (i=0; i < original.subject.length; i++) {
                    subjects.push({field: {subject: original.subject[i]}});
                };
                if (subjects.length > 1) {
                    if (original.subject_and) {
                        queries.push({bool: {must: subjects}});
                    } else {
                        queries.push({bool: {should: subjects}});
                    };
                } else {
                    queries.push(subjects[0]);
                };
            };
            if (queries.length > 1) {
                query = {bool: {must: queries}};
            } else {
                query = queries[0];
            };

            if (original.meta_type) {
                query = {
                    filtered : {
                        query : query,
                        filter : {
                            terms : {
                                metaType : original.meta_type || [],
                                execution : "or",
                                _cache : true
                            }
                        }
                    }
                }
            };

            return {
                size: BATCH_SIZE,
                sort: [sort],
                query: query,
                highlight: {
                        fields: {
                            title: {number_of_fragments: 0},
                            description: {fragment_size: 150, number_of_fragments: 3}
                        }
                    },
                fields: ['url', 'title', 'description', 'metaType']
            };
        };

        var do_search = function(query, from) {
            // Form up any query here
            query['from'] = from || 0;
            $.ajax({
                url: get_url(),
                type: 'POST',
                crossDomain: true,
                dataType: 'json',
                success: function(data) {
                    var notifies = data.hits.total ? results : empty_results;
                    for (var i=0, len=notifies.length; i < len; i++) {
                        notifies[i](data.hits, from || 0);
                    }
                },
                error: function () {
                    for (var i=0, len=empty_results.length; i < len; i++) {
                        empty_results[i]();
                    }
                },
                data: JSON.stringify(query)
            });
            return query;
        };

        return {
            subscribe: function(plugin) {
                if (plugin.onempty !== undefined) {
                    empty_results.push(plugin.onempty);
                };
                if (plugin.onresult !== undefined) {
                    results.push(plugin.onresult);
                };
            },
            scroll: function(index) {
                if (previous_query !== null) {
                    do_search(previous_query, index);
                };
            },
            search: function(term) {
                previous_query = do_search(build_query(term));
            }
        };
    };

    var CountDisplayPlugin = function($count, loading) {
        return {
            onempty: function() {
                loading(false);
                $count.text('0');
            },
            onresult: function(data) {
                loading(false);
                $count.text(data.total);
            }
        };
    };

    var ResultDisplayPlugin = function($result, $empty) {
        var trailing_punctuation_re = /^[;,.\s]*([\S\s]*?)[;,.\s]*$/;

        var trim_punctuation = function(string) {
            var match = string.match(trailing_punctuation_re);
            if (match) {
                return match[1];
            }
            return string;
        };
        var truncate_text = function(string) {
            return string.length > 256 ? string.substr(0, 256) + ' &hellip;' : string;
        };

        var get_entry = function(entry) {
            var title = entry.fields.title,
                description = null,
                i;

            if (entry.highlight !== undefined) {
                if (entry.highlight.title !== undefined) {
                    title = entry.highlight.title[0];
                };
                if (entry.highlight.description !== undefined) {
                    description = '&hellip; ';
                    for (i=0; i < entry.highlight.description.length; i++) {
                        description += trim_punctuation(entry.highlight.description[i]) + ' &hellip; ';
                    };
                };
            };
            if (description === null) {
                if (entry.fields.description) {
                    description = truncate_text(entry.fields.description);
                } else {
                    description = '';
                };
            };

            var mt = entry.fields.metaType;

            return {
                title: title,
                description: description,
                url: entry.fields.url,
                meta_type: mt.replace(/^\s+|\s+$/g, '').replace(/\s+/g,'-').toLowerCase()
            };
        };

        return {
            onempty: function() {
                $result.hide();
                $empty.show();
            },
            onresult: function(data) {
                var entry, i, len;

                $empty.hide();
                $result.empty();
                $result.show();
                for (i=0, len=data.hits.length; i < len; i++) {
                    entry = get_entry(data.hits[i]);
                    $result.append(
                        '<dt class="contenttype-'
                            + entry.meta_type + '"><a href="'
                            + entry.url + '">' + entry.title + '</a></dt><dd>'
                            + entry.description + '</dd>'
                    );
                };
            }
        };
    };

    var BatchDisplayPlugin = function($batch, update) {
        var PAGING    = 3,
            NO_LEAP   = 0,
            PRE_LEAP  = 1,
            POST_LEAP = 2,

            $prev = $('span.previous'),
            $next = $('span.next'),

            $prev_a = $('span.previous a'),
            $next_a = $('span.next a'),

            $prev_size = $('span.previous a span span'),
            $next_size = $('span.next a span span'),

            link_to = function (opt) {
                var $item;

                if (opt.current) {
                    $item = $('<span class="esGeneratedBatch current"> ' + opt.page + ' </span>');
                } else {
                    $item = $('<a class="esGeneratedBatch" href=""> ' + opt.page + ' </a>');

                    if (opt.leap) {
                        var $leap = $('<span>&hellip;</span>');
                        if (opt.leap == PRE_LEAP) {
                            $item.prepend($leap);
                        } else {
                            $item.append($leap);
                        }
                    };

                    $item.bind('click', function () {
                        update((opt.page - 1) * BATCH_SIZE);
                        return false;
                    });
                };
                return $item;
            };

        return {
            onempty: function() {
                $batch.hide();
            },
            onresult: function(data, current) {
                $batch.hide();

                if (data.total <= BATCH_SIZE) {
                    return;
                }

                $batch.children('.esGeneratedBatch').remove();

                var page_count = Math.ceil(data.total / BATCH_SIZE);
                var current_page = Math.ceil(current / BATCH_SIZE) + 1;
                var $current = link_to({page : current_page, current: true});

                $current.insertAfter($next);

                for (var i = PAGING; i >= 1; i--) {
                    if (current_page - i <= 1) {
                        continue;
                    }
                    link_to({page : current_page - i}).insertBefore($current);
                };

                for (var i = PAGING; i >= 1; i--) {
                    if (current_page + i >= page_count) {
                        continue;
                    }
                    link_to({page : current_page + i}).insertAfter($current);
                };

                if (current_page > 1) {
                    var first_leap = current_page - PAGING > 2 ? POST_LEAP : NO_LEAP;
                    $prev_size.text(BATCH_SIZE);
                    $prev_a.unbind();
                    $prev_a.bind('click', function () { update(current - BATCH_SIZE); return false });
                    $prev.show();
                    link_to({page: 1, leap: first_leap}).insertAfter($next);
                } else {
                    $prev.hide();
                };

                if (current_page < page_count) {
                    var last_leap = current_page + PAGING < (page_count - 2) ? PRE_LEAP : NO_LEAP;
                    var next_size = Math.min(data.total - (current_page * BATCH_SIZE), BATCH_SIZE);
                    $next_size.text(next_size);
                    $next_a.unbind();
                    $next_a.bind('click', function () { update(current + BATCH_SIZE); return false });
                    $next.show();
                    link_to({page: page_count, leap: last_leap}).appendTo($batch);
                } else {
                    $next.hide();
                };

                $batch.show();
            }
        };
    };

    $(document).ready(function() {
        $('.esSearchForm').each(function() {
            var $form = $(this),

                $resultHeader = $form.find('h1.esResultHeader'),
                $searchResults = $form.find('dl.searchResults'),
                $listingBar = $form.find('div.listingBar'),
                $emptyResults = $form.find('div.emptySearchResults'),
                $loader = $resultHeader.find('img'),
                $count = $form.find('span.searchResultsCount'),
                $discreet = $form.find('span.discreet'),

                $options = $form.find('div.esSearchOptions'),
                search = ElasticSearch($form);

            var $query = $form.find('input.searchPage'),
                $author = $form.find('input#Contribs'),
                $subject = $form.find('select#Subject'),
                $subject_operator = $form.find('input#Subject_and'),
                $since = $form.find('select#created'),
                $published = $form.find('input#Published'),
                $publishedBefore = $form.find('input#Published_before'),
                $current = $form.find('input#CurrentFolderOnly'),
                $button = $form.find('input[type=submit]'),
                $sort = $form.find('select#sort_on'),
                $meta_types = $form.find('input[id^="portal_type_"]'),
                options = $options.hasClass('expanded'),
                previous = null,
                timeout = null;

            var loading = function (load) {
                load ? $count.hide() : $count.show();
                load ? $loader.show() : $loader.hide();
                load ? $discreet.hide() : $discreet.show();
                load ? $emptyResults.hide() : $emptyResults.show();

                $resultHeader.show();
            };

            var hide_search_results = function () {
                $resultHeader.hide();
                $emptyResults.hide();
                $listingBar.hide();
                $searchResults.hide();
            };

            var scroll_search = function(index) {
                if (timeout !== null) {
                    clearTimeout(timeout);
                    timeout = null;
                };
                search.scroll(index);
            };

            var schedule_search = function(force) {
                if (timeout !== null) {
                    clearTimeout(timeout);
                };

                var search_term = $query.val();

                if (search_term.length) {
                    loading(true);
                } else {
                    loading(false);
                    hide_search_results();
                    return;
                }

               timeout = setTimeout(function () {
                    var query = {term: search_term},
                        meta_types = [];

                    if (options) {
                        query['contributors'] = $author.val();
                        query['subject'] = $subject.val();
                        query['subject_and'] = $subject_operator.is(":checked");
                        query['created'] = $since.val();
                        query['sort'] = $sort.val();
                        query['published_year'] = $published.val();
                        query['published_before'] = $publishedBefore.is(":checked");

                        if ($current.is(":checked")) {
                            query['url'] = $current.val();
                        };

                        $meta_types.each(function () {
                            var $field = $(this);
                            if ($field.is(':checked')) {
                                meta_types.push($field.val());
                            };
                        });
                        if (meta_types.length) {
                            query['meta_type'] = meta_types;
                        };
                    };

                    if (force || query.term != previous && !options) {
                        search.search(query);
                        previous = query.term;
                    };
                    timeout = null;
                }, 200);
            };

            // hide result counter if we've not had a search yet
            hide_search_results();

            search.subscribe(CountDisplayPlugin($count, loading));
            search.subscribe(ResultDisplayPlugin($searchResults, $emptyResults));
            search.subscribe(BatchDisplayPlugin($listingBar, scroll_search));

            $form.find('a.esSearchOptions').bind('click', function (event) {
                options = !options;
                $options.slideToggle();
                event.preventDefault();
            });

            $button.bind('click', function(event) {
                schedule_search(true);
                event.preventDefault();
            });
            $options.delegate('input,select', 'change', schedule_search);
            $query.bind('change', schedule_search);
            $query.bind('keyup', schedule_search);
            if ($query.val() || options) {
                if (options) {
                    $options.show();
                    $options.removeClass('expanded');
                };
                schedule_search(true);
            };
        });
    });

})(jQuery);
