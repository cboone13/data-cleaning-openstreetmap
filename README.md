
# 🗺️ MapMend: Cleaning and Analyzing OpenStreetMap Data for Fayetteville, NC

**Project Type:** Data Wrangling / Data Quality Assessment  
**Tools:** Python, Regular Expressions, Microsoft SQL Server  
**Dataset:** OpenStreetMap XML Extract (Fayetteville, NC)

---

## 📌 Project Overview

In this project, I applied data munging and wrangling techniques to clean and analyze OpenStreetMap data for **Fayetteville, North Carolina**. Using Python and SQL Server, I audited the data for validity, consistency, completeness, and formatting errors.

The cleaned data is intended to improve the quality of OpenStreetMap (OSM) contributions and demonstrate my ability to transform raw semi-structured data into a usable format for geographic analysis.

---

## 🌍 Map Area

📍 Fayetteville, NC, United States  
🔗 [View Map](https://www.openstreetmap.org/export#map=13/35.0311/-78.9520)

---

## 🛠️ Key Cleaning Tasks

### 🏷️ Street Name Abbreviations

Audited and standardized street names using regular expressions and a mapping dictionary.

```python
def audit_street_type(self, street_name):
    m = self.street_type_re.search(street_name)
    if m:
        street_type = m.group()
        if street_type not in self.expected:
            self.street_types[street_type].add(street_name)
```

Example:  
- **"Ft. Bragg rd"** → **"Fort Bragg Road"**

### 🔡 Inconsistent Casing

Normalized street names and address fields for consistent casing.

### 🏙️ City Name Errors

Flagged and fixed records where the `addr:city` field was improperly filled with full addresses instead of city names.

---

## 🧪 Data Exploration with SQL Server

### 📊 Sort Cities by Count

```sql
SELECT nt.[value] AS City, COUNT(*) AS Count
FROM node_tags nt
WHERE nt.[key] LIKE '%city'
GROUP BY nt.[value]
ORDER BY Count DESC;
```

### 🍔 Top 10 Fast Food Restaurants

```sql
SELECT TOP (10) nt1.[value], COUNT(*) AS Count
FROM node_tags nt1
JOIN (
    SELECT DISTINCT nt2.[id]
    FROM node_tags nt2 
    WHERE [value] = 'fast_food'
) nt2 ON nt1.[id] = nt2.[id]
WHERE nt1.[key] = 'name'
GROUP BY nt1.[value]
ORDER BY Count DESC;
```

---

## 📁 File Sizes

| File               | Size     |
|--------------------|----------|
| interpreter.osm    | 63.4 MB  |
| nodes.csv          | 23.9 MB  |
| nodes_tags.csv     | 0.26 MB  |
| ways.csv           | 2.6 MB   |
| ways_nodes.csv     | 7.95 MB  |

---

## 📈 Summary Statistics

- **Number of Nodes:** 281,214  
- **Number of Ways:** 42,006  
- **Unique Users:** 198  

### 🧑‍💻 Top Contributors

| User              | Contributions |
|------------------|----------------|
| MrNyanUniverse   | 203,779        |
| woodpeck_fixbot  | 36,990         |
| jumbanho         | 31,240         |
| tekim            | 15,384         |
| bdiscoe          | 4,624          |

### 👤 Users with Only 1 Contribution

```sql
SELECT COUNT(*) 
FROM (
  SELECT [user], COUNT(*) as count
  FROM (
    SELECT [user] FROM nodes 
    UNION ALL 
    SELECT [user] FROM ways
  ) e
  GROUP BY e.[user]
  HAVING COUNT(*) = 1
) c;
```

Result: **56 users**

---

## 🔎 Observations & Suggestions

While the address data was relatively clean, the dataset lacks depth in categories like internet access, religious institutions, and business types. Supplementing with U.S. Census data would significantly enhance this dataset’s utility for demographic and commercial insights — though limitations around granularity and timeliness should be considered.

---

## 🧠 Additional Queries

### 🌐 Internet Access Counts

```sql
SELECT [value], COUNT(*) AS Number
FROM node_tags
WHERE [key] = 'internet_access'
GROUP BY [value]
ORDER BY Number DESC;
```

| Value | Count |
|-------|-------|
| no    | 1     |

### ✝️ Religious Denominations

```sql
SELECT TOP (10) [value] AS Denomination, COUNT(*) AS Count
FROM node_tags
WHERE [key] = 'denomination'
GROUP BY [value]
ORDER BY Count DESC;
```

| Denomination | Count |
|--------------|-------|
| baptist      | 3     |

### 🛐 Largest Religions

```sql
SELECT TOP (10) nt1.[value] AS Religion, COUNT(*) AS Count
FROM node_tags nt1
JOIN (
    SELECT DISTINCT nt2.[id]
    FROM node_tags nt2 
    WHERE [value] = 'place_of_worship'
) nt2 ON nt1.[id] = nt2.[id]
WHERE nt1.[key] = 'religion'
GROUP BY nt1.[value]
ORDER BY Count DESC;
```

| Religion  | Count |
|-----------|-------|
| christian | 42    |

---

## 🧾 Conclusion

The Fayetteville OSM dataset had relatively few structural issues. However, the lack of deeper metadata — such as internet access or community facilities — limits its broader applicability. Further enrichment could improve its usefulness in planning and analysis.

---

## 📚 Resources

- [OpenStreetMap](https://www.openstreetmap.org/)
- [Udacity: OpenStreetMap Case Study](https://www.udacity.com)
- [Stack Overflow](https://stackoverflow.com)
- [Jeswin George GitHub Reference](https://github.com/jeswingeorge/Wrangle-Openstreetmap-data)

---

## ⚖️ License

This project is open source under the [MIT License](LICENSE).
