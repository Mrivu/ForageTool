# ForageTool
Submission for HY-TKT20019

This application is an addition to my D&D campaign, which allows players to search, discover and manage plants.

- Admin users can add plant packages, which update the available plants for all users.
- Users are required to log in due to the existence of an admin account and database information.
- Users can view and sort all acquired plants.
- Found plants can be deleted or turned into potions.
- Users can search for individual plants by name.
- The application displays statistics on found plants.
- Found plants can be sorted into different "Folders"
- Users can create notes on found plants.


# Current state
- Currently, the application supports a login and register system. The distinction between Admin users and regular users does not yet exist.
- Plant packages can be downloaded by uploading a plant JSON. You can toggle if the download overrides any existing plants. 
- These plants are exported to the catalogue, a listing of all available plants. These plants can be further edited or removed.
- The catalogue also supports a search system, with a filter drop-down box based on which attribute the user wants to find the plant.
- The catalogue also orders the plants, but currently only alphabetically.
- The search keyword and filter are stored in the session for a satisfying user experience and reset once the user leaves the catalogue.

# Future plans
- Add Admin system and restrict user actions
- Add inventory for found plants and user page

# Guide
- A valid plant JSON can be found under the plant Packages folder at "/ForageTool/PlantPackages/EvervastPlants2.json".
- Run "flask run" at "/ForageTool/app"