import "@react-three/fiber";

declare module "@react-three/fiber" {
  interface ThreeElements {
    group: any;
    mesh: any;
    sphereGeometry: any;
    meshStandardMaterial: any;
    ambientLight: any;
    pointLight: any;
  }
}