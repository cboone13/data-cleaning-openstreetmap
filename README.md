# udacity_data_wrangling_open_street_maps
Udacity data analyst nanodegree - use data munging techniques, such as assessing the quality of the data for validity, accuracy, completeness, consistency and uniformity, to clean the OpenStreetMap data for a part of the world that you care about. Finally, use Microsoft SQL Server as the data schema to complete your project.

### Map Area
Fayetteville, NC, United States
- [https://www.openstreetmap.org/export#map=13/35.0311/-78.9520]

This map is of the town and surrounding area that I currently live in, so I’m interested to see how bad the data in this area is. Upon completion I'd like to see my contribution applied to OpenStreetMap.org.

### Problems Encountered in the Map
After downloading a map portion of the Fayetteville, NC area I ran a small python script to conduct a brief audit of the data. The following is what my audit found:

- Abbreviated street names
- Inconsistant casing to streets
- 'addr:city' has bad data (Full address entered as city)

#### Abbreviated Street Names

Using my fullRun.py script, I parsed through the osm file and audited the street names to check if the street name is abbreviated or not. If abbreviated, I checked it against my mapping dictionary and replaced the abbreviation with the full street type before adding the record to a list for writing. I use regular expressions to check for invalid characters as well as taking the street name and checking to see if it is in my expected list.

```python 
    def audit_street_type(self, street_name):
        # Check if street name is in expected mapping. 
        # If not, add it to street_type list.
        m = self.street_type_re.search(street_name)
        if m:
            street_type = m.group()
            if street_type not in self.expected:
                self.street_types[street_type].add(street_name)
```

This gave me a list of addr:street that needed to be updated so that:
"Ft. Bragg rd"
Would become:
"Fort Bragg Road"


### Data Overview and Additional Ideas
This section contains basic information about the dataset, the Microsoft SQL queries used and other ideas about the dataset.

#### Sort cities by count, descending

```
From Microsoft SQL Server:
SELECT
	 nt.[value] AS 'City'
	,COUNT(*) as 'Count' 
FROM node_tags nt
WHERE nt.[key] LIKE '%city'
GROUP BY nt.[value]
ORDER BY  count DESC;
```

This query can be used to verify that there are no cities or misspellings within the dataset.
The information returned looks like this: 

From Microsoft SQL Server:
***City***     ***Count***
Fayetteville       38
Hope Mills          3

#### Top 10 Most Frequently Occuring Fast Food Restraunts

```
From Microsoft SQL Server:
    SELECT TOP (10)
        nt1.[value]
        ,COUNT(*) as 'Count'
    FROM [dbo].[node_tags] nt1
    JOIN (
          SELECT DISTINCT
                nt2.[id] 
          FROM [dbo].[node_tags] nt2 
          WHERE [value] ='fast_food'
          ) nt2
          ON nt1.[id] = nt2.[id]
    WHERE nt1.[key] = 'name'
    GROUP BY nt1.[value]
    ORDER BY 'Count' DESC
```

We can determine the top 10 most frequently occuring fast food restaraunts in the dataset.
First we have to query to get the name of the fast food restraunt then by rejoining to the table
we are able to get only those venues that have the value of fast_food.

#### File sizes
```
interpreter.osm ....... 63.4 MB
nodes.csv ............. 23.9 MB
nodes_tags.csv ........ 0.26 MB
ways.csv .............. 2.6 MB
ways_nodes.cv ......... 7.95 MB  
```  

#### Number of nodes
```
From Microsoft SQL Server:
    SELECT  
        COUNT( *)
    FROM [dbo].[nodes]	
```
281214

#### Number of ways
```
From Microsoft SQL Server:
    SELECT  
        COUNT(*)
    FROM [dbo].[ways]	
```
42006

#### Number of unique users
```
From Microsoft SQL Server:
    SELECT 
        COUNT(DISTINCT(u.[uid]))          
    FROM (
          SELECT [uid] 
          FROM [dbo].[nodes] 
          UNION ALL 
          SELECT [uid] 
          FROM [dbo].[ways]
          ) u
```
198

#### Top 5 contributing users
```
From Microsoft SQL Server:
    SELECT TOP (5)
        u.[user]
        ,COUNT(*) as 'Number of Contributions'
    FROM (
         SELECT 
            [user] 
         FROM [dbo].[nodes] 
         UNION ALL 
         SELECT 
            [user] 
         FROM [dbo].[ways]
         ) u
    GROUP BY u.[user]
    ORDER BY 'Number of Contributions' DESC

```

***user***           ***Number of Contributions***
MrNyanUniverse          203779
woodpeck_fixbot         36990
jumbanho                31240
tekim                   15384
bdiscoe                 4624
 
 
#### Number of users having only 1 post
```
From Microsoft SQL Server:
    SELECT 
        COUNT(*) 
    FROM
        (SELECT 
            e.[user]
            ,COUNT(*) as 'count'
         FROM (
               SELECT 
                    [user]
               FROM [dbo].[nodes] 
               UNION ALL 
               SELECT 
                    [user] 
               FROM [dbo].[ways]
               ) e
         GROUP BY e.[user]
         HAVING COUNT(*) = 1) c

     
```
56

### Observation and suggestion
From some of the sql query results when trying to find a count of the different denominations, internet access, and
places of workship I saw that the result were very small in proportion to the area. For example the number of places flagged without internet was only 1 where as nothing came back as places with internet. Data like this can be obtained from the U.S. Census data so including this data along with populations and demographics would increase the benefits of the dataset. Being able to see the average household age or the population of specifics areas could help businesses target their advertising and know in what ways they can better tailor their product to the area. Including this information would, however provide come complexity and issues. Though most can be obtained from the U.S. Census, the data will ineveitably be dated as the census is not a yearly proccess. It would also be difficult to determine how to calculate the total population for areas. as being able to select a custom area could exclude data that is meant for a specific area. This could be avoided by having records that contain only municipality data so the user will know that the totals are a representation of the city proper as opposed to their custom zone.

### Number of Places with Interent Access
```
From Microsoft SQL Server:
    SELECT TOP (10)
        [value] 
        ,COUNT(*) as 'Number'
    FROM [node_tags]
    WHERE [key] = 'internet_access'
    GROUP BY [value]
    ORDER BY 'Number' DESC
```

***value***     ***Number***
no                    1
### Top 10 denominations

```
From Microsoft SQL Server:
    SELECT TOP (10)
        [value] AS 'Denomination'
        ,COUNT(*) as 'Count'
    FROM [node_tags]
    WHERE [key] = 'denomination'
    GROUP BY [value]
    ORDER BY 'Number' DESC
```
***Denomination***     ***Count***
baptist                     3

### Largest Religions
```
From Microsoft SQL Server:
    SELECT TOP (10)
        nt1.[value] AS 'Religion'
        ,COUNT(*) as 'Count'
    FROM [dbo].[node_tags] nt1
    JOIN (
          SELECT DISTINCT
                nt2.[id] 
          FROM [dbo].[node_tags] nt2 
          WHERE [value] ='place_of_worship'
          ) nt2
          ON nt1.[id] = nt2.[id]
    WHERE nt1.[key] = 'religion'
    GROUP BY nt1.[value]
    ORDER BY 'Count' DESC
```

***Religion***     ***Count***
christian              42


### Conclusion

After reviewing the data for this area of Fayetteville, NC it can be seen that the streets and addresses did not require a large amount of cleaning. I did find it interesting to see how little data was reported when looking deeper than the house or business address. The lack of types of business as well as the number of records returned when not looking for a street address specifically was surprisingly small making the data unreliable for a more in depth analysis of census type information when the ability to include that information is present.

### Resources

https://www.openstreetmap.org/

https://www.stackoverflow.com

https://www.udacity.com
	- Case Study: OpenStreetMap Data" lesson

https://github.com/jeswingeorge/Wrangle-Openstreetmap-data