import React, { useEffect, useState } from 'react';
import { MapContainer, TileLayer, Marker, Polyline, CircleMarker, Popup } from 'react-leaflet';
import '../App.css';
import "leaflet/dist/leaflet.css";
import { Icon } from 'leaflet';
import plane from '../images/plane.png';
import { io } from 'socket.io-client';

<head>
  <link rel="stylesheet" href="https://unpkg.com/leaflet@1.7.1/dist/leaflet.css"
   integrity="sha512-xodZBNTC5n17Xt2atTPuE1HxjVMSvLVW9ocqUKLsCC5CXdbqCmblAshOMAS6/keqq/sMZMZ19scR4PsZChSR7A=="
   crossorigin=""/>
</head>

let socket = io("wss://tarea-3-websocket.2021-1.tallerdeintegracion.cl", {path: '/flights'});

const planeIcon = new Icon({
  iconUrl: plane,
  iconSize: [25, 25]
});


const Map = () => {

  const [originDestinations, setOriginDestinations] = useState([]);
  const [flightsInfo, setFlightsInfo] = useState([]);
  const [trayectories, setTrayectories] = useState([]);
  const [gotFlightsInfo, setGotFlightsInfo] = useState(false);

  socket.emit("FLIGHTS");
  useEffect(() => {
    socket.on("FLIGHTS", (obj) => {
      if (!gotFlightsInfo) {
        obj.forEach(element => {
          setOriginDestinations(prev => [...prev, [element.origin, element.destination, element.code]]);
          setFlightsInfo(prev => [...prev, element]);
        });
        setGotFlightsInfo(true);
      };
    });

    return () => {
      socket.off();
    }
  });

  useEffect(() => {
    socket.on("POSITION", (obj) => {
      setTrayectories(prev => ([...prev, obj]));
      flightsInfo.forEach(element => {
        if (element.code === obj.code) {
          element.origin = obj.position;
          setFlightsInfo(flightsInfo);
        }
      });
    });

    return () => {
      socket.off();
    }
  });

  const getOriginLat = (code) => {
    let lat;
    originDestinations.forEach(element => {
      if (element[2] === code) {
        lat = element[0][0].toPrecision(4);
      };
    });
    return lat;
  };

  const getOriginLng = (code) => {
    let lng;
    originDestinations.forEach(element => {
      if (element[2] === code) {
        lng = element[0][1].toPrecision(4);
      };
    });
    return lng;
  };

  return (
    <div id="mapid">
      <MapContainer
        center={[0, 0]}
        zoom={2}
        style={{height: "60vh"}}
        >
        <TileLayer
          attribution='&copy; <a href="http://osm.org/copyright">OpenStreetMap</a> contributors'
          url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
        />
        {flightsInfo.map(element => {
          return (
            <Marker position={element.origin} icon={planeIcon}>
              <Popup>{element.code}</Popup>
            </Marker>
          );
        })}
        {originDestinations.map(element => {
          return (
            <Polyline positions={[element[0], element[1]]} />
          );
        })};
        {originDestinations.map(element => {
          return (
            <CircleMarker center={element[0]}/>
          );
        })}
        {originDestinations.map(element => {
          return (
            <CircleMarker center={element[1]}/>
          );
        })}
        {trayectories.map(element => {
          return (
            <CircleMarker
            center={element.position}
            color="red"
            radius={2}
            />
          );
        })}
      </MapContainer>
      <div className="flights">
        {flightsInfo.map(element => {
          return (
            <div className="flightInfo">
              <h3>Vuelo {element.code}</h3>
              <b>Aerolínea:</b> {element.airline}<br/>
              <b>Origen:</b> [Lat, Lng] = [{getOriginLat(element.code)}, {getOriginLng(element.code)}]<br/>
              <b>Destino:</b> [Lat, Lng] = [{element.destination[0].toPrecision(4)}, {element.destination[1].toPrecision(4)}]<br/>
              <b>Avión:</b> {element.plane}<br/>
              <b>Nº de asientos:</b> {element.seats}<br/>
              <b>Pasajeros: </b> {element.passengers.map((passenger, idx) => (
                <ul id="ulId" key={idx.toString()}>{passenger.name} - {passenger.age} años</ul>
              ))}
            </div>
          );
        })}
      </div>
    </div>
  )
}

export default Map;