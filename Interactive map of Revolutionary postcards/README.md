# Interactive map of Revolutionary postcards
- Most of the existing research on postcards is focused on their visual presentation. Tourism studies and historical studies cover a wide range of subjects in which postcards, especially images of postcards are used to explore perceptions of places, cultures, and certain groups of people.
- However, postcards contain more information than just images and texts.
- 261 postcards, mostly sent during the 1917 Revolution in Russia, were found and provided in digital form by Maria Tychilina, an employee of the Mayakovsky Library. Maria is engaged in genealogical research. For genealogical research, postcards, organized and presented on an interactive map with a timeline, are a source of genealogical information.
- When we present postcards sent in the context of certain historical periods and global events, we need to focus on specific dates that can be compared with data on the dates of historical events. An equally important factor is the understanding and visual interpretation of the geographical locations of the place of sending and receiving postcards, the name and status of the sender and addressee, as well as the address of the place where the postcard was subsequently found. This allows for the spatial data analysis and to obtain new conclusions, visions and cultural data.
- Therefore, it was necessary to implement the Digital Humanities project in the format of a web resource, which systematized and geo-visualized postcards sent during the revolution.
### Goals and objectives of the project
- The research goals of the Digital Humanities project are systematization of postcards to search for ancestors and displaying postcards on a map with a timeline for interpreting postcards as a source of cultural and historical information. The project promotes educational, cultural and tourism activities related to the events of the February and October revolutions of 1917-1918 that took place in Petrograd.
##### The project tasks:
1. Search for the most convenient, effective and relevant technological solutions for geovisualization of digital objects of cultural and historical heritage. 
2. Systematization of postcards, formation of a database of postcards.
3. Creation of a digital interactive exhibition that can be used by historians, culturologists, art historians, students and employees of international scientific laboratories of digital humanities research, people interested in history, genealogy researchers and others.
4. Georeferencing of the map of Petrograd and the database of postcards to the actual map of St. Petersburg.
5. Creating a timeline on the map to filter postcards by year.
6. Application of the methodology for analyzing spatially distributed data - converting coordinates from a geographical reference system into various metric systems.
7. Publication of a web resource on the Internet.
### Getting Started
##### Implementation of the project on Omeka 
To use the Omeka platform with the connection of the necessary plugins and the use of storage for loading objects, you need to host the site on the omeka.net servers or install the API Omeka Classic.
Omeka Classic has the following system requirements:
- Linux operating system
- Apache HTTP server (with mod_rewrite enabled)
- MySQL version 5.0 or greater
- PHP scripting language version 5.4 or higher (with mysqli and exif extensions installed)
- ImageMagick image manipulation software (for resizing images)

Because hosting on omeka.net costs up to $1000 per year and still has limited functionality, it is more effective to use third-party hosting services. To solve the problem, the most effective solution is to set up LAMP and Omeka using Amazon Linux AMI.
##### Setting up a web server for installing Omeka API
Setting up LAMP and Omeka using the Amazon Linux AMI consists of 5 steps:
1.	Setting Up Linux Machine in Amazon Web Services (AWS). 
2.	Connecting to the EC2 Instance Using SSH and Upgrading Linux.
3.	Installing the Apache Server and Creating a Sample HTML Page.
4.	Installing the MySQL Server and Setting up MySQL Secure Connection.
5.	Creating Database and User for Omeka Application.

To Set Up Linux Machine in Amazon Web Services (AWS) follow instructions in [file 1](https://github.com/dh-center/Projects2022/blob/main/Interactive%20map%20of%20Revolutionary%20postcards/Setting%20up%20LAMP%20and%20Omeka%20using%20the%20Amazon%20Linux%20AMI.md).
To complete other steps follow instructions in [file 2](https://github.com/dh-center/Projects2022/blob/main/Interactive%20map%20of%20Revolutionary%20postcards/Terminal%20code%20for%20setting%20up%20a%20web%20server%20to%20install%20Omeka%20API.md). 

##### Convert Excel files to CSV files, Import CSV files to Omeka
To simplify and speed up the process of adding postcard table data to the Omeka collection, you need to convert data from Excel to CSV, and then import CSV files into Omeka database using a plugin "CSV Import". In order to do this, you have to brought the data in Excel to a common format and filled in the gaps.

##### Connecting the map of Petrograd with a timeline to Omeka
- To create an interactive map for a collection of postcards in Omeka, I installed the Neatline plugin. In Neatline, I created an exhibition where I transferred all the items from the Omeka collection. 
- To make the project more visual and interesting, I needed to find a map of Petrograd in 1917 and convert the map image into a .tiff georeferenced format. The Neatline plugin allows you to add a map layer with a .tiff image. In order for the layer to be displayed on the map, you have to create and add a WMS Address. To do this, I used the Map Warper service.
- Because the exhibition contains about 300 postcards, manual processing of addresses and adding points to the map takes a lot of time, so I needed to find a solution for adding geolocation using Spatial Data, namely Geometry (Well-Known Text). WKT is a text format for describing features. 
- If we take the address coordinates, for example, from the Yandex.Maps service, the projection of the coordinates will be WGS 84 (EPSG:4326). Neatline only accepts spatial data in pseudo-Mercator projection (EPSG:3857). To transform the projection, I used the MyGeodata Cloud service.

### Usage
- To enter the platform, you need to open a browser and enter the URL = http://Public.IP.Address/omeka/admin
- Enter login and password

![alt text](https://github.com/dh-center/Projects2022/blob/main/Interactive%20map%20of%20Revolutionary%20postcards/Screenshots/Authorization.png)

- To use the interactive map go to the Neatline tab

![alt text](https://raw.githubusercontent.com/dh-center/Projects2022/main/Interactive%20map%20of%20Revolutionary%20postcards/Screenshots/Neatline.png)

- Select an exhibition with a map and click Fullscreen View

![alt text](https://raw.githubusercontent.com/dh-center/Projects2022/main/Interactive%20map%20of%20Revolutionary%20postcards/Screenshots/Interactive%20map.png)

### Author

##### Nikita Galkin
- email: galkins@niuitmo.ru
- Telegram: galkinsn
