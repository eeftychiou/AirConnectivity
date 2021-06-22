#Pagerak Air Connectivity Indicator and optimizer

Air Connectivity Indicator using pagerank.
Can load Eurocontrol R&D Data to calculate connectivity indicator using weighted Pagerank and other network metrics.
Weight can be a simple connection, proportional to the onwards connectivity at the destination airport or proportional to the passenger capacity of the flight(TODO)

TODO:
Inject flights into the database and analyse the effect it has on the Destination and Departure Aerodrome
Identify optimal flights to maximmize onwards/inwards connectivity and the indicator value for the involved aerodromes.

Data can be downloaded from:
https://www.eurocontrol.int/dashboard/rnd-data-archive
