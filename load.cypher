LOAD CSV FROM "file:///nodes.txt" AS line
CREATE (p:Point {
    id: toInteger(line[0]), 
    latitude: toFloat(line[1]),
    longitude: toFloat(line[2])
    }); 

CREATE INDEX FOR (p:Point) ON (p.id)

LOAD CSV FROM "file:///edges.txt" AS line
MATCH (from_p:Point { id: toInteger(line[1])}),(to_p:Point { id: toInteger(line[2])})
CREATE (from_p)-[:CONNECTED_TO { id: toInteger(line[0]) }]->(to_p);
LOAD CSV FROM "file:///nodes_poi.txt" AS line
CREATE (p:Point {
    id: toInteger(line[0]), 
    latitude: toFloat(line[1]),
    longitude: toFloat(line[2]),
    poi: 1
    }); 
LOAD CSV FROM "file:///edges_poi.txt" AS line
MATCH (from_p:Point { id: toInteger(line[1])}),(to_p:Point { id: toInteger(line[2])})
CREATE (from_p)-[:CONNECTED_TO { id: toInteger(line[0]) }]->(to_p);
