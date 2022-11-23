## Basic API tests using CURL 

### NOTES 
- in order for these commands to run, you first need to make sure the flask app is running on your local machine

### Get list of patients 
```
curl http://0.0.0.0/api/patients/list
```

### Get a specific patient 
```
curl http://0.0.0.0/api/patients/214a80e5
```

### Adding a new patient
```
curl -H "Content-Type: application/json" -X POST -d '{"mrn": "343sdsd232", "first_name": "hants", "last_name": "williams"}' http://0.0.0.0/api/patient

```

### Delete a existing patient 
```
curl http://0.0.0.0/api/patient/343sdsd232 -X DELETE
```

### Delete a existing patient - GUI
```
curl http://0.0.0.0/delete/343sdsd232 -X POST
```