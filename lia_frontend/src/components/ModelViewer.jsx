import React from 'react'
import { Canvas } from '@react-three/fiber'
import { useGLTF, OrbitControls, Stage } from '@react-three/drei'
import * as THREE from 'three'

function Model() {
  const { scene, animations } = useGLTF('/LiaRobot.gltf')
  return <primitive object={scene} />
}

function ModelViewer({ className }) {
  return (
    <React.StrictMode>
      <div className={`model-viewer-container ${className}`} style={{ width: '100%', height: '100%', background: '#1a1a1a' }}>
        <Canvas>
          <Stage environment="night">
            <ambientLight intensity={0.5} />
            <pointLight position={[10, 10, 10]} intensity={1} />
            <Model />
          </Stage>
          <OrbitControls />
        </Canvas>
      </div>
    </React.StrictMode>
  )
}

export default ModelViewer