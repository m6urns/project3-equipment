# project3-equipment

## Ideas for analysis

- Does the authorization/supply of new weapons systems/operational parameters impact equipment losses?
    - Need to extract historic data
    - Not possible due to format of data provided by Oryx, would need to be collecting with every update
    - Would need to correlate with this sheet: https://docs.google.com/spreadsheets/d/1bngHbR0YPS7XH1oSA1VxoL4R34z60SJcR3NxguZM9GI/edit?gid=0#gid=0
    - We could also pull dailies from web archive: https://web.archive.org/web/20240104001559/https://www.oryxspioenkop.com/2022/02/attack-on-europe-documenting-equipment.html
    - Web archive seems like best option for this
        - Would need to extract and export counts for each day, write and store them, then utilize them as needed. 
        - Does the current scraper also work on web-archive content? Yes! Seems to work well, so we just need to loop through dailies. Write to csv in an archive folder, and then we can compile dataset from there
    - Compile dailies into daily totals by type, for visualization
- How do equivalent systems perform when used by UKR/RUS?
- Compare tank survivability, by tank type. Example: Are RUs T-34 more vulnerable than UKRs T-34?
- Overlay major battles/offensives to overall losses
- Analyze survivability of primary MBT, Abraham, Chieftain, etc verses RU T-80

![alt text](https://github.com/m6urns/project3-equipment/blob/matt/plots/all_types_over_time.png?raw=true "All Types") 

![alt text](https://github.com/m6urns/project3-equipment/blob/matt/plots/T-72B_losses.png?raw=true "T72-B Losses")

![alt text](https://github.com/m6urns/project3-equipment/blob/matt/plots/BMP-2(K)_losses.png?raw=true  "BMP-2(K)")