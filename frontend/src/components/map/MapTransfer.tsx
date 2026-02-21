import { MapContainer, TileLayer, Marker, Popup } from "react-leaflet";
import { type LatLngExpression } from "leaflet";
import "leaflet/dist/leaflet.css";

const position: LatLngExpression = [40.6139, -74.209]; // North, East

const MapTransfer = () => {
  return (
    <MapContainer
      center={position}
      zoom={7}
      className="mr-8 mb-5 h-auto w-screen rounded-lg "
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
