import { MapContainer, TileLayer, Marker, Popup } from "react-leaflet";
import { type LatLngExpression } from "leaflet";
import "leaflet/dist/leaflet.css";

const position: LatLngExpression = [28.6139, 77.209]; // Delhi

const MapTransfer = () => {
  return (
    <MapContainer
      center={position}
      zoom={5}
      style={{ height: "100%", width: "100%" }}
      className="mr-5"
    >
      <TileLayer
        // attribution="&copy; OpenStreetMap contributors"
        url="https://{s}.tile.openstreetmap.fr/hot/{z}/{x}/{y}.png"
      />

      <Marker position={position}>
        <Popup>Delhi</Popup>
      </Marker>
    </MapContainer>
  );
};

export default MapTransfer;
