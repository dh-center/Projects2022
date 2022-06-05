Once you've found an image to georeference, you need to launch ArcMap and set up your environment:

1. Add a base map by clicking on File > Add Data > Add Basemap. 

2. Add the static image that you want rectify by clicking on File > Add Data > Add Data. Navigate to the location of the image, select it, and click “Add.” (Note: If the folder containing the image is not already available in the dropdown menu to the right of “Look in,” you may have to “connect” to the folder by clicking on the folder icon with the black “+” symbol in the toolbar to the right. Select the folder, click “OK,” and the folder should become available in the main dropdown menu.) If you get a popup asking if you want to generate pyramids, click “No,” and if you get an alert labeled “Unknown Spatial Reference,” click “OK” (ArcMap is just reacting to the fact that the image doesn’t have existing geo-coordinates).

3. Enable the Georeferencing toolbar by clicking Customize > Toolbars > Georeferencing. 

4. Move to the rough location of the image that’s being rectified by using the navigation controls at the left of the top toolbar to zoom the base map to the approximate location and bounds of the historical map.

5. Show the static image by clicking on Georeferencing > Fit To Display.

Now, the actual rectification. All this entails is creating a series of associations (at least two, as many as ~15-20) between points on the static image and points on the real-geography base layer. As you add points, ArcMap will automatically pan, rotate, scale, and ultimately “warp” the image to match the underlying base layer.

1. Lay a positioning point: To lay the first point, click on the “Add Control Points” button in the Georeferencing toolbar and click at the exact position on the historical map that you want to use as the starting point. Then, without clicking down on the map viewport again, move the cursor over to the “Table of Contents” pane and check off the historical map, leaving just the base layer visible. Then, click on the location on the base layer that corresponds to the original location on the historical map.

Once you’ve clicked for a second time, the dotted line between the two clicks will disappear. Display the historical map again by checking the box next to its title in the “Table of Contents.” The image will now be anchored onto the base layer around the location of the first point association.

2. Lay a scaling and rotation point: Next, pick another easily-mappable point on the historical map, this time ideally near the edges of the image, or at least some significant distance from the first point. Follow the same steps of clicking on the historical map, hiding the historical map, clicking on the corresponding location on the base layer, and then re-enabling the historical map to see the effect.

At this point, you already have a minimally rectified image - the second point will both scale the image down to roughly correct proportions and rotate the image to the correct orientation. From this point forward, adding more points will make the rectification increasingly accurate and granular by “warping” the image, like a sheet of rubber, to fit the lattice of points as accurately as possible.

As you work (especially in cases where you’re laying down a lot points) experiment with different “transformation” algorithms by clicking Georeferencing > Transformations and selecting one of the five options (1st Order Polynomial, 2nd Order Polynomial, etc). Behind the scenes, these algorithms represent different computational approaches to “fitting” the image based on the set of control points - some of the transformations will leave the image roughly polygonal, whereas others will dramatically “warp” the shape of the image to make it conform more accurately to the point associations. Depending on the type of image you’re working with and its accuracy relative to the base layer, different transformations will produce more or less pleasing results. 

Once you’re done laying points, save off the image as a georeferenced .tiff file by clicking Georeferencing > Rectify. As desired, change the filename and target directory, and click “Save.”
