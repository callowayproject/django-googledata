from gdata.analytics import service
import datetime, time
from django.core.cache import cache
from django.conf import settings as global_settings
from settings import LOGIN, PASSWORD, CACHE_LENGTH, CALL_LENGTH



def cache_get(key):
    """
    Modified cache getting derived from MintCache http://www.djangosnippets.org/snippets/793/
    
    Since the remote call to google can take several seconds, we don't want a 
    dog pile.
    """
    packed_val = cache.get(key)
    if packed_val is None:
        return None
    try:
        val, refresh_time, refreshed = packed_val
    except:
        if global_settings.DEBUG:
            raise
        else:
            return None
    if (time.time() > refresh_time) and not refreshed:
        # Store the stale value while the cache revalidates for another CALL_LENGTH seconds.
        cache_set(key, val, timeout=CALL_LENGTH, refreshed=True)
        return None
    return val


def cache_set(key, val, timeout=CACHE_LENGTH, refreshed=False):
    """
    Modified cache setting derived from MintCache http://www.djangosnippets.org/snippets/793/
    
    Since the remote call to google can take several seconds, we don't want a 
    dog pile.
    """
    refresh_time = timeout + time.time()
    real_timeout = timeout + CALL_LENGTH
    packed_val = (val, refresh_time, refreshed)
    return cache.set(key, packed_val, real_timeout)


def get_account_list():
    acct_client = service.AnalyticsDataService()
    acct_client.ClientLogin(LOGIN, PASSWORD)
    acct_list = acct_client.GetAccountList()
    
    return [(item.tableId[0].text, item.title.text) for item in acct_list.entry]


def get_top_pages(ga_table_id, num_results=10, days_past=1, path_filter='', title_sep=None):
    """
    Return the top ``num_results`` viewed pages for the past ``days_past`` days.
    
    You can filter the results by path (e.g. only pages whose path starts with
    news: ``/news/*`` ). Because the title is returned and can contain extra data
    such as web site name, the ``title_sep`` character will split the title into 
    chunks. Set ``title_sep`` to ``None`` to turn it off.
    
    :param ga_table_id: 
        The Google Analytics table id, in the form 'ga:1234567'
    :type ga_table_id: 
        ``string``
    :param num_results: 
        The number of top pages to retreive. **Default:** 10
    :type num_results: 
        ``integer``
    :param days_past:
        The easy way to set the date range for selecting the top pages. The ending
        date is always right now. The starting date is ``days_past`` days ago.
        **Default:** 1
    :type days_past:
        ``integer``
    :param path_filter:
        The regular expression for filtering the results based on their path.
        For example '/categories/sports/*' could find the top sports page.
    :type path_filter:
        ``string``
    :param title_sep:
        The character to use to split the returned page title into chunks. This
        makes it easy to get the "real" title of the page. For example, if your
        page title is ``Article Title | Web Site Name``, set ``title_sep`` to 
        "|" and it will return ``['Article Title','Web Site Name'] as the page
        title. Set ``title_sep`` to ``None`` to have it return the whole string.
        **Default:** ``None``
    :type title_sep:
        ``string`` or ``None``
    :returns:
        The page titles and path for the top pages
    :rtype:
        Either ``[ {'title': ['pagetitle1','pagetitle2'], 'path': '/path/to/page', 'pageviews': 1000 }, ... ]`` if 
        ``title_sep`` is a ``string`` or ``[ {'title': 'pagetitle1 | pagetitle2', 'path': '/path/to/page', 'pageviews': 1000 }, ... ]``
        if ``title_sep`` is ``None``.
    """
    cache_key = "get_top_pages.%s.%s.%s.%s.%s" % (ga_table_id, num_results, days_past, path_filter, title_sep)
    cache_results = cache_get(cache_key)
    
    if cache_results:
        return cache_results
    
    acct_client = service.AnalyticsDataService()
    acct_client.ClientLogin(LOGIN, PASSWORD)
    
    sdate = datetime.date.today() - datetime.timedelta(days=days_past)
    start_date = sdate.isoformat()
    end_date = datetime.date.today().isoformat()
    dimensions = "ga:pageTitle,ga:pagePath"
    metrics = "ga:pageviews"
    sort = "-ga:pageviews"
    results = 10
    
    if path_filter:
        filter_str = "ga:pagePath=~%s" % path_filter
    else:
        filter_str = ''
    
    data = acct_client.GetData(
        ids=ga_table_id,
        dimensions=dimensions,
        metrics=metrics,
        sort=sort,
        start_date=start_date,
        end_date=end_date,
        filters=filter_str,
        max_results=results
    )
    
    results = []
    for item in data.entry:
        result_item = {'path': item.pagePath, 'pageviews': item.pageviews}
        if title_sep:
            result_item['title'] = [x.strip() for x in str(item.pageTitle).split(title_sep)]
        else:
            result_item['title'] = item.pageTitle
        
        results.append(result_item)
    cache_set(cache_key)
    return results

#get_top_pages('ga:6488592', path_filter="/news/*")
print get_top_pages('ga:22442888', title_sep='|')
#print get_account_list()