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
    * [__imagesRange()__](#camerasimagesrange)
    * [showImage()](#camerasshowimage)
    * [__showImages()__](#camerasshowimages)
    * [__downloadImages()__](#camerasdownloadimages)
  
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
  
### Cameras.imagesRange

Return the image times available for a given camera and given range of times in the media cache. The media cache contains all recent images archived by Helios, either for internal analytics or for end user recording purposes.

__Cameras.imagesRange(__ camera_id, start_time, end_time, limit=500 __)__
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
  
### Cameras.showImage

Return a single image from the media cache. The media cache contains all recent images archived by Helios, either for internal analytics or for end user recording purposes.

__Cameras.showImage(__ camera_id, time, delta=900000 __)__
* Parameters
	* camera_id: *str*
		* Camera ID.
	* time: *str*
		* Time
	* delta: *int*
		* Max acceptable difference (in milliseconds) between the requested time and the image time. If a match is not found, a 404 status will be returned. If not specified, a default value of 900000 (i.e. 15 minutes) is assumed.
* Reteurns
    * JSON: *dictionary*
        * key: "url"
        * 302 redirect to a signed URL where the camera image can be retrieved. The signed URL is valid for 15 minutes.

### Cameras.showImages

Return a single images from the media cache for a given time range. The media cache contains all recent images archived by Helios, either for internal analytics or for end user recording purposes.

__Cameras.showImages(__ camera_id, start_time, delta=900000 __)__
* Parameters
    * camera_id: *str*
        * Camera ID.
	* times: *list*
		* Image times to search for the given camera_id.
	* delta: *int*
		* Max acceptable difference (in milliseconds) between the requested time and the image time. If a match is not found, a 404 status will be returned. If not specified, a default value of 900000 (i.e. 15 minutes) is assumed.
* Returns
    * JSON: *dictionary*
        * key: "url"
		* 302 redirect to a signed URL where the camera image can be retrieved. The signed URL is valid for 15 minutes.
	
### Cameras.downloadImages

Download images from URLs.

__Cameras.downloadImages(__ urls, out_dir=None, return_image_data=False __)__
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
	* [__downloadImages()__](#observationsdownloadimages)
  
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

__Observations.show(__ observation_id __)__
* Parameters
    * observation_id: *str*
        * Observation ID.
* Returns
    * GeoJSON feature: *dictionary*
        * keys: "geometry", "type", "id", and "properties". 
		
### Observations.preview

Return a preview image for the observation. This API call will attempt to filter out unusable images (e.g. full image text/logos, etc.) and will return the most recent image for the observation time period.

__Observations.preview(__ observation_id __)__
* Parameters
	* observation_id: *str*
* Returns
	* Image URL

### Observations.downloadImages

Download images from URLs.

__Observations.downloadImages(__ urls, out_dir=None, return_image_data=False __)__
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
    * [showImage()](#collectionsshowimage)
    * __[showImages()](collectionsshowimages)__
    * __[downloadImages()](#collectionsdownloadimages)__
    * [addImage()](#collectionsaddimage)
    * __[addImages()](#collectionsaddimages)__
    * [removeImage()](#collectionsremoveimage)
    * __[removeImages()](#collectionsremoveimages)__
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
	
### Collections.showImage

Return a single image from a collection.

__Collections.showImage(__ id_var, image_name __)__
* Parameters
    * id_var: *str*
        * Collection ID.
    * image_name: *str*
        * Image Name.
* Reteurns
    * JSON: *dictionary*
        * 302 redirect to a signed URL where the image can be retrieved. The signed URL is valid for 15 minutes.
        * keys: "url"

	
### Collections.showImages

Return a all images from a collection.

__Collections.showImages(__ collection_id, image_names __)__
* Parameters
    * collection_id: *str*
        * Collection ID.
	* image_names: *list*
		* Image names to search for the given collection_id.
* Returns
    * JSON: *dictionary*
        * key: "url"
		* 302 redirect to a signed URL where the camera image can be retrieved. The signed URL is valid for 15 minutes.
	
### Collections.downloadImages

Download images from URLs.

__Collections.downloadImages(__ urls, out_dir=None, return_image_data=False __)__
* Parameters
    * urls: *list*
		* List of image urls to be downloaded.
	* out_dir: *str, optional*
		* If a path to an output directory is given, images will be saved to the directory.
	* return_image_data: *bool, optional*
		* If true, image data will be read into a numpy array and returned.
* Returns
	* None or list of numpy arrays.

### Collections.addImage

Add a single image to a collection.

__Collections.addimage(__ collection_id, img_url __)__
* Parameters
    * collection_id: *str*
        * Collection ID.
    * img_url: *str*
	    *  Image url to be added to collection.
* Reteurns
    * JSON: *dictionary* 
        * key: "ok"
   
### Collections.addImages

Add multiple images to a collection.

__Collections.addImages(__ collection_id, img_list __)__
* Parameters
    * collection_id: *str*
        * Collection ID.
    * img_list: *list*
        * List of image URLs.
* Returns:
    * JSON: *list of dictionaries*
        * key: "ok"

### Collections.removeImage

Remove a single image from a collection.

__Collections.removeImage(__ collection_id, img_url __)__
* Parameters
    * collection_id: *str*
        * Collection ID.
    * img_url: *str*
        * Single image URL.
* Returns
    * JSON: *dictionary*
        * key: "ok"
	
### Collections.removeImages

Remove multiple images from a collection.

__Collections.removeImage(__ collection_id, img_url __)__
* Parameters
    * collection_id: *str*
        * Collection ID.
    * img_url: *str*
        * Single image URL.
* Returns
    * JSON: *list of dictionaries*
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