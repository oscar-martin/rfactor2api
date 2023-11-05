# rFactor2 HTTP API

This project exposes an HTTP server to read rfactor2 live data.

It relies on different projects with some changes to adapt them to this use case:

- To read rfactor2 data: https://github.com/s-victor/pyRfactor2SharedMemory 
- To support for converting from ctypes.Structure to JSON objects: https://github.com/rinatz/ctypes_json

## Runtime dependency

This depends on The Iron Wolf’s rF2 Shared Memory Map Plugin, download it from here:
https://forum.studio-397.com/index.php?threads/rf2-shared-memory-tools-for-developers.54282/

## Run it [in progress]

It is recommended to create a [virtualenv](https://virtualenv.pypa.io/en/latest/) to run this.

Run rfactor2.

For the moment, use this command to launch it. In a future, an exe file will be created.

```shell
uvicorn main:app
```

It will create a HTTP server at http://localhost:8000 with two relevant endpoints:

* http://localhost:8000/scoring/ 

    It will output a JSON object created out of this struct: https://github.com/TheIronWolfModding/rF2SharedMemoryMapPlugin/blob/master/Monitor/rF2SMMonitor/rF2SMMonitor/rF2Data.cs#L846

* http://localhost:8000/telemetry/

    It will output a JSON object created out of this struct: https://github.com/TheIronWolfModding/rF2SharedMemoryMapPlugin/blob/master/Monitor/rF2SMMonitor/rF2SMMonitor/rF2Data.cs#L831

