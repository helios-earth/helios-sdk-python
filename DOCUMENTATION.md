# DEPRECATION WARNING
There is no guarantee that this documentation is up-to-date.  This will soon
be replaced by Sphinx docs and will ultimately be removed.

# Helios-SDK-Python
# Documentation

Note: Bold-faced classes and methods are extensions on the core capabilities.

------------------
* [Alerts](#alerts)
* [Cameras](#cameras)
* [Observations](#observations)
* [Collections](#collections)
------------------

## Alerts
[Documentation](https://helios.earth/developers/api/alerts/)

* Alerts
    * [index()](#alertsindex)
    * [show()](#alertsshow)

### Alerts.index

Return a list of alerts matching the provided spatial, text, or metadata filters.

__Alerts.index(__ **kwargs __)__
* Parameters
    * kwargs: 
        * Any keyword arguments found in the [documentation](https://helios.earth/developers/api/alerts/#index)
* Returns
    * GeoJSON feature collections: *list of dictionaries*
        * keys: "type", "features", and "properties".
		* Warning: If the maximum-skip value of 4000 is exceeded while querying, truncated results will be returned.
  
### Alerts.show

Return the attributes for a single alert.

__Alerts.show(__ alert_id __)__
* Parameters
    * alert_id: *str*
        * Alert ID. 
* Returns
    * GeoJSON feature: *dictionary*
        * keys: "geometry", "properties", "type", "id", and "bbox"

------------------

## Cameras
[Documentation](https://helios.earth/developers/api/cameras/)

* Cameras
    * [index()](#camerasindex)
    * [show()](#camerasshow)
    * [images()](#camerasimages)
    * [__images_range()__](#camerasimages_range)
    * [show_image()](#camerasshow_image)
    * [__download_images()__](#camerasdownload_images)
  
### Cameras.index

Return a list of cameras matching the provided spatial, text, or metadata filters.

__Cameras.index(__ **kwargs __)__
* Parameters
    * kwargs: 
        * Any keyword arguments found in the [documentation](https://helios.earth/developers/api/cameras/#index)
* Returns
    * GeoJSON feature collections: *list of dictionaries*
        * keys: "type", "features", "bbox", and "properties".
		* Warning: If the maximum-skip value of 4000 is exceeded while querying, truncated results will be returned.
  
### Cameras.show

Return the attributes for a single camera.

__cameras.show(__ camera_id __)__
* Parameters
    * camera_id: *str*
        * Camera ID.
* Returns
    * GeoJSON feature: *dictionary*
        * keys: "geometry", "type", "id", and "properties". 

### Cameras.images

Return the image times available for a given camera in the media cache. The media cache contains all recent images archived by Helios, either for internal analytics or for end user recording purposes.

__Cameras.images(__ camera_id, start_time, limit=500 __)__
* Parameters
    * camera_id: *str*
        * Camera ID
    * start_time: *str*
    * limit: *int* 
        * Optional limit on query.  Default value of 500 is the maximum.
* Returns
    * JSON: *dictionary*
        * keys: "total" and "times"
  
### Cameras.images_range

Return the image times available for a given camera and given range of times in the media cache. The media cache contains all recent images archived by Helios, either for internal analytics or for end user recording purposes.

__Cameras.images_range(__ camera_id, start_time, end_time, limit=500 __)__
* Parameters
    * camera_id: *str*
        * Camera ID.
    * start_time: *str*
    * end_time: *str*
    * limit: *int* 
        * Optional limit on query.  Default value of 500 is the maximum.
* Returns
    * JSON: *dictionary*
        * keys: "total" and "times"
  
### Cameras.show_image

Return image URLs from the media cache. The media cache contains all recent images archived by Helios, either for internal analytics or for end user recording purposes.

__Cameras.show_image(__ camera_id, times __)__
* Parameters
	* camera_id: *str*
		* Camera ID.
	* times: *str* or *list*
		* Times
* Returns
    * JSON: *dictionary*
        * key: "url"
        * 302 redirect to a signed URL where the camera image can be retrieved. The signed URL is valid for 15 minutes.
	
### Cameras.download_images

Download images from URLs.

__Cameras.download_images(__ urls, out_dir=None, return_image_data=False __)__
* Parameters
    * urls: *list*
		* List of image urls to be downloaded.
	* out_dir: *str, optional*
		* If a path to an output directory is given, images will be saved to the directory.
	* return_image_data: *bool, optional*
		* If true, image data will be read into a numpy array and returned.
* Returns
	* None or list of numpy arrays.
	
------------------
  
## Observations
[Documentation](https://helios.earth/developers/api/observations/)

* Observations
    * [index()](#observationsindex)
    * [show()](#observationsshow)
	* [preview()](#observationspreview)
	* [__download_images()__](#observationsdownload_images)
  
### Observations.index

Return a list of sensor observations matching the provides spatial, text, or metadata filters

__Observations.index(__ **kwargs __)__
* Parameters
    * kwargs: 
        * Any keyword arguments found in the [documentation](https://helios.earth/developers/api/observations/#index)
* Returns
    * GeoJSON feature collections: *list of dictionaries*
        * keys: "type", "features", "bbox", and "properties".
		* Warning: If the maximum-skip value of 4000 is exceeded while querying, truncated results will be returned.
  
### Observations.show

Return the attributes for a single observation.

__Observations.show(__ observation_ids __)__
* Parameters
    * observation_id: *str*
        * Observation ID.
* Returns
    * GeoJSON feature: *dictionary*
        * keys: "geometry", "type", "id", and "properties". 
		
### Observations.preview

Return preview images for observations. This will return the most recent image for the observation time period.

__Observations.preview(__ observation_ids __)__
* Parameters
	* observation_ids: *str* or *list*
* Returns
	* Image URL(s)

### Observations.download_images

Download images from URLs.

__Observations.download_images(__ urls, out_dir=None, return_image_data=False __)__
* Parameters
    * urls: *list*
		* List of image urls to be downloaded.
	* out_dir: *str, optional*
		* If a path to an output directory is given, images will be saved to the directory.
	* return_image_data: *bool, optional*
		* If true, image data will be read into a numpy array and returned.
* Returns
	* None or list of numpy arrays.
------------------
  
## Collections
[Documentation](https://helios.earth/developers/api/collections/)

* Collections
    * [index()](#collectionsindex)
    * [show()](#collectionsshow)
    * [create()](#collectionscreate)
    * __[images()](#collectionsimages)__
    * [show_image()](#collectionsshow_image)
    * __[download_images()](#collectionsdownload_images)__
    * [add_image()](#collectionsadd_image)
    * [remove_image()](#collectionsremove_image)
    * __[copy()](#collectionscopy)__
  
### Collections.index

Return a list of collections matching the provided text or metadata filters.

__Collections.index(__ **kwargs __)__
* Parameters
    * kwargs: 
        * Any keyword arguments found in the [documentation](https://helios.earth/developers/api/collections/#index)
* Returns
    * JSON: *list of dictionaries*
        * keys: "results", "total", "skip", and "limit".
		* Warning: If the maximum-skip value of 4000 is exceeded while querying, truncated results will be returned.

### Collections.show

Return the attributes and image list for a single collection.

__Collections.show(__ collection_id, limit=200, marker=None __)__
* Parameters
    * id_var: *str*
        * Collection ID string.
    * limit: *int, optional*
        * Number of image names to be returned with each response. Defaults to 20. Max value of 200 is allowed.
    * marker: *str, optional*
        * Pagination marker. If the marker is an exact match to an existing image, the next image after the marker will be the first image returned. Therefore, for normal linked list pagination, specify the last image name from the current response as the marker value in the next request. Partial file names may be specified, in which case the first matching result will be the first image returned.
* Returns
    * JSON: *dictionary*
        * keys: "_id", "name", "description", "tags", "created_at", "updated_at", "images", "limit", and "marker".
  
### Collections.create

Create a new collection.

__Collections.create(__ name, description, tags=None __)__
* Parameters
    * name: *str*
        * Name for new collection.
    * description: *str*
    * tags: *list or str, optional*
        * List of strings (tags), or string of comma-separated tags.
* Returns
    * TODO

### Collections.images

Returns the image names in a given collection. 

__Collections.images(__ collection_id, camera=None, old_flag=False __)__
* Parameters
    * collection_id: *str*
        * Collection ID.
    * camera: *str, optional*
        * Camera ID: If provided, then only image names from that camera will be returned.
    * old_flag: *bool, optional*
        * If true, then image storage name will not look for the md5 hashes at the beginnning of file names.
* Returns
    * JSON: *dictionary*
        * keys: "images" and "total".
	
### Collections.show_image

Return image URLs from a collection.

__Collections.show_image(__ collection_id, image_names __)__
* Parameters
    * collection_id: *str*
        * Collection ID.
    * image_names: *str* or *list*
        * Image Name(s).
* Reteurns
    * JSON: *dictionary*
        * 302 redirect to a signed URL where the image can be retrieved. The signed URL is valid for 15 minutes.
        * keys: "url"
		
### Collections.download_images

Download images from URLs.

__Collections.download_images(__ urls, out_dir=None, return_image_data=False __)__
* Parameters
    * urls: *list*
		* List of image urls to be downloaded.
	* out_dir: *str, optional*
		* If a path to an output directory is given, images will be saved to the directory.
	* return_image_data: *bool, optional*
		* If true, image data will be read into a numpy array and returned.
* Returns
	* None or list of numpy arrays.

### Collections.add_image

Add a images to a collection.

__Collections.add_image(__ collection_id, data __)__
* Parameters
    * collection_id: *str*
        * Collection ID.
    * data: *list of dict*
	    *  List of dictionaries containing any of the following keys:
	        * camera_id
	        * camera_id, time
	        * observations_id
	        * collection_id, image
	    * e.g. `data = [{'camera_id': 'cam_01', time: '2017-01-01T00:00:000Z'}]`
* Returns
    * JSON: *dictionary* 
        * key: "ok"

### Collections.remove_image

Remove a single image from a collection.

__Collections.remove_image(__ collection_id, names __)__
* Parameters
    * collection_id: *str*
        * Collection ID.
    * names: *str* or *list*
        * Image name(s) to remove from the specified collection.
* Returns
    * JSON: *dictionary*
        * key: "ok"

### Collections.copy

Copy a collection and its contents to a new collection.

__Collections.copy(__ collection_id, new_collection_name __)__
* Parameters
    * collection_id: *str*
        * Collection ID.
    * new_collection_name: *str*
        * Name for the new collection.
* Returns
    * JSON: *list of dictionaries*
        * key: "ok"