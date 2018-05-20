from IPython.core.debugger import Tracer
from astroquery.query import BaseQuery
from astroquery.utils import parse_coordinates
from astropy.coordinates import SkyCoord
import html # to unescape, which shouldn't be neccessary but currently is
from .registry import Registry
from . import utils
from astropy.table import Table, vstack
import requests, io, astropy



class ConeClass(BaseQuery):
    def __init__(self):
        super(ConeClass, self).__init__()
        self._TIMEOUT=3 # seconds to timeout
        self._RETRIES = 3 # total number of times to try

    def query(self, service, coords, radius, **kwargs):
        """Basic cone search query function 

        Input coords should be either a single string, a single
        SkyCoord object, or a list. It will then loop over the objects
        in the list, assuming each is a single source. Within the
        _one_cone_search function, it then expects likewise a single
        string, a single SkyCoord object, or list of 2 as an RA,DEC
        pair.

        Input service can be a string URL a single row
        of an astropy Table. 

        """
            
##        #Tracer()()
##        # Get the list of URLs that provide matching cone searches 
##        #
##        if services is None: 
##            try:
##                services=Registry.query(service_type='cone',**kwargs)
##            except:
##                raise 
##        elif type(services) is astropy.table.row.Row:
##            # The user handed one row of an astropy table, e.g., from
##            # a registry query, make it look like a list
##            services=Table(services)
##        elif type(services) is str:
##            services=Table([{'access_url':services}])
##        elif isinstance(services, Table):
##            # In this case, assume they checked the table and query all of them (?)
##            max_services=len(services)
##        else:
##            assert isinstance(services, Table), "ERROR: Don't understand services given; expect a string URL or an astropy Table result from a Registry query."
##
##
##        assert len(services) <= max_services, "ERROR: You're asking to query more than {} services; max_services is set to {}. If you really want to do more, then set the max_services parameter to a larger number.".format(len(services),max_services)
    
        if type(service) is str:
            service={"access_url":service}

            
        if type(coords) is str or isinstance(coords,SkyCoord):
            coords=[coords]
        assert type(coords) is list, "ERROR: Give a coordinate object that is a single string, a list/tuple (ra,dec), a SkyCoord, or a list of any of the above."

        if type(radius) is not list:
            inradius =  [radius]*len(coords)
        else:
            inradius = inradius            
            assert len(inradius) == len(coords), 'Please give either single radius or list of radii of same length as coords.'

        # Construct list of dictionaries, each with the parameters needed 
        # for the function you're calling in the query_loop:
        params=[{'coords':c,'radius':inradius[i]} for i,c in enumerate(coords)] 
        return utils.query_loop(self._one_cone_search, service=service, params=params)
        

    def _one_cone_search(self, coords, radius, service):
        if ( type(coords) is tuple or type(coords) is list) and len(coords) == 2:
            coords=parse_coordinates("{} {}".format(coords[0],coords[1]))
        elif type(coords) is str:
            coords=parse_coordinates(coords)
        else:
            assert isinstance(coords,SkyCoord), "ERROR: cannot parse input coordinates {}".format(coords)

        params = {'RA': coords.ra.deg, 'DEC': coords.dec.deg, 'SR':radius}
        
        response=utils.try_query(service,get_params=params,timeout=self._TIMEOUT,retries=self._RETRIES)

        return utils.astropy_table_from_votable_response(response)


##      def _astropy_cone_table_from_votable_response(self,response):
##          """Need one of these for each class, or one generic standardize()? 
##          
##          For now, just simple conversion. Store the raw XML
##          from the query as well as the URL in the meta data.
##          In future, standardize the columns by replacing the 
##          column name with the UCD if there is one.
##          """
##          #Tracer()()
##          try:
##              table= Table.read(io.BytesIO(response.content))
##              # Store the raw response content and the url queried
##              #  in the meta data of the table. Make its value a list,
##              #  because this will allow us to concatenate (vstack)
##              #  different queries and merge the metadata
##              
##              # TODO:  Consider whether we want to save the raw data for non-debug cases.
##              table.meta['xml_raw']=[response.content]
##              table.meta['url']=[response.url]
##              return table
##          except:
##              # TODO: if this was a real exception, as opposed to being just an empty result, we should put
##              # the exception info into the metadata or somewhere in the table.  Consider more detailed info here too.
##              empty=Table(masked=True)
##              empty.meta['xml_raw']=[response.content]
##              empty.meta['url']=[response.url]
##              return empty

Cone=ConeClass()

