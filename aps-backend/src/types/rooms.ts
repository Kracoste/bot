export interface RoomSummary {
  name: string;
  area_m2: number | null;
  perimeter_m: number | null;
  bbox: {
    min: [number, number];
    max: [number, number];
  };
  source: string;
}

export interface RoomsPayload {
  fileId: string;
  rooms: RoomSummary[];
}
