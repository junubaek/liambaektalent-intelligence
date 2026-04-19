import re

path = r'C:\Users\cazam\Downloads\안티그래비티_온톨로지 사전\ontology_hub_template.html'
with open(path, 'r', encoding='utf-8') as f:
    content = f.read()

content = content.replace('let hoveredNode = null;', 'let hoveredNode = null, selectedNodeId = null, offset = 0;')

new_code = '''
function init3D() {
    const container = document.getElementById('scene-container');
    const wrap = document.getElementById('map-view');
    const width = wrap.clientWidth;
    const height = wrap.clientHeight;

    scene = new THREE.Scene();
    camera = new THREE.PerspectiveCamera(50, width / height, 1, 30000);
    renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true });
    renderer.setSize(width, height);
    renderer.setPixelRatio(window.devicePixelRatio);
    container.appendChild(renderer.domElement);

    controls = new THREE.OrbitControls(camera, renderer.domElement);
    controls.enableDamping = true; 
    controls.dampingFactor = 0.05;
    controls.autoRotate = true; 
    controls.autoRotateSpeed = 0.3;

    raycaster = new THREE.Raycaster();
    mouse = new THREE.Vector2();

    const starfieldGeo = new THREE.BufferGeometry();
    const starfieldPos = [];
    for(let i=0; i<2500; i++) {
        starfieldPos.push((Math.random()-0.5)*15000, (Math.random()-0.5)*15000, (Math.random()-0.5)*15000);
    }
    starfieldGeo.setAttribute('position', new THREE.Float32BufferAttribute(starfieldPos, 3));
    scene.add(new THREE.Points(starfieldGeo, new THREE.PointsMaterial({ color: 0xffffff, size: 2, transparent: true, opacity: 0.3 })));

    scene.add(new THREE.AmbientLight(0xffffff, 0.3));
    const scanLight = new THREE.PointLight(0x58a6ff, 1.5);
    scanLight.position.set(0, 1000, 0);
    scene.add(scanLight);

    createGalaxyCluster();
    camera.position.set(1800, 1200, 2800);
    animate3D();

    window.addEventListener('resize', onWindowResize3D);
    container.addEventListener('mousemove', onMouseMove3D);
    container.addEventListener('click', onClick3D);
}

function createLabel(text) {
    const div = document.createElement('div');
    div.className = 'label-hud';
    div.textContent = text;
    document.getElementById('map-view').appendChild(div);
    return div;
}

let activeLabels = [];
function clearLabels() {
    activeLabels.forEach(item => item.el.remove());
    activeLabels = [];
}

function updateLabelsPos() {
    activeLabels.forEach(item => {
        const vector = item.pos.clone();
        vector.project(camera);
        const container = document.getElementById('scene-container');
        const rect = container.getBoundingClientRect();
        const x = (vector.x * .5 + .5) * rect.width;
        const y = (vector.y * -.5 + .5) * rect.height;
        item.el.style.left = x + 'px';
        item.el.style.top = (y - 25) + 'px';
    });
}

function zoomMap(dir) {
    if (!camera || !controls) return;
    const v = new THREE.Vector3();
    v.subVectors(controls.target, camera.position).normalize();
    camera.position.addScaledVector(v, dir * 500);
    controls.update();
}

function createGalaxyCluster() {
    const layerSpacing = 350;
    const worldRadius = 1400; 
    const spreadMultiplier = 1.3;

    LC_META.forEach((meta, idx) => {
        const yBase = -(idx * layerSpacing) + (layerSpacing * 3);
        const stepNodes = NODES.filter(n => {
            let nLc = Array.isArray(n.lc) ? n.lc[0] : n.lc;
            if (!nLc) nLc = "Architecture";
            return nLc === meta.key;
        });

        stepNodes.forEach((node) => {
            const angle = Math.random() * Math.PI * 2;
            const dist = (300 + Math.sqrt(Math.random()) * (worldRadius - 300)) * spreadMultiplier;
            const x = Math.cos(angle) * dist;
            const z = Math.sin(angle) * dist;
            const y = (yBase + (Math.random() - 0.5) * 300) * spreadMultiplier; 

            const color = getStackColorHex(node.stack);
            
            const core = new THREE.Mesh(
                new THREE.SphereGeometry(7, 16, 16),
                new THREE.MeshBasicMaterial({ color: 0xffffff })
            );
            
            const glow = new THREE.Mesh(
                new THREE.SphereGeometry(15, 16, 16),
                new THREE.MeshPhongMaterial({ 
                    color: color, transparent: true, opacity: 0.5, 
                    emissive: color, emissiveIntensity: 2.5 
                })
            );

            const group = new THREE.Group();
            group.add(core); group.add(glow);
            group.position.set(x, y, z);
            group.userData = { id: node.id, name: node.name, stack: node.stack, color: color };
            
            scene.add(group);
            nodeMeshes.push(group);
        });
    });

    NODES.forEach(node => {
        const src = nodeMeshes.find(m => m.userData.id === node.id);
        if (!src) return;
        (node.rel || []).forEach(tid => {
            const tgt = nodeMeshes.find(m => m.userData.id === tid);
            if (tgt) {
                const curve = new THREE.QuadraticBezierCurve3(
                    src.position,
                    new THREE.Vector3(
                        (src.position.x + tgt.position.x) / 2 + (Math.random() - 0.5) * 200,
                        (src.position.y + tgt.position.y) / 2 + 300,
                        (src.position.z + tgt.position.z) / 2 + (Math.random() - 0.5) * 200
                    ),
                    tgt.position
                );

                const points = curve.getPoints(30);
                const geometry = new THREE.BufferGeometry().setFromPoints(points);
                const line = new THREE.Line(geometry, new THREE.LineBasicMaterial({ 
                    color: 0xffffff, transparent: true, opacity: 0.02 
                }));
                
                line.userData = { sourceId: node.id, targetId: tid };
                scene.add(line);
                lineMeshes.push(line);
            }
        });
    });
}

function updateHighlights() {
    const activeId = selectedNodeId || (hoveredNode ? hoveredNode.userData.id : null);
    
    nodeMeshes.forEach(n => {
        const isSelf = n.userData.id === activeId;
        const nodeData = NODES.find(x => x.id === activeId);
        const isRelated = nodeData && ((nodeData.rel||[]).includes(n.userData.id) || NODES.find(x => x.id === n.userData.id)?.rel?.includes(activeId));
        
        if (activeId) {
            n.children[1].material.opacity = (isSelf || isRelated) ? 0.9 : 0.03;
            n.scale.setScalar(isSelf ? 3 : (isRelated ? 1.8 : 0.5));
            n.children[1].material.emissiveIntensity = isSelf ? 5 : (isRelated ? 3 : 1);
        } else {
            n.children[1].material.opacity = 0.5; n.scale.setScalar(1); n.children[1].material.emissiveIntensity = 2.5;
        }
    });

    lineMeshes.forEach(l => {
        if (activeId) {
            const isPath = l.userData.sourceId === activeId || l.userData.targetId === activeId;
            l.material.opacity = isPath ? 0.8 : 0.001;
            l.material.color.set(isPath ? 0x58a6ff : 0xffffff);
        } else {
            l.material.opacity = 0.02; l.material.color.set(0xffffff);
        }
    });
}

function animate3D() {
    animReq3D = requestAnimationFrame(animate3D);
    if(controls) controls.update();
    if(renderer) renderer.render(scene, camera);
    if(activeLabels.length > 0) updateLabelsPos();

    offset += 0.005;
    lineMeshes.forEach((l, i) => {
        if (l.material.opacity > 0.1) {
            l.position.y = Math.sin(offset + i) * 2;
        }
    });
}

function onMouseMove3D(event) {
    if(tab !== "map") return;
    const container = document.getElementById("scene-container");
    const rect = container.getBoundingClientRect();
    
    mouse.x = ((event.clientX - rect.left) / rect.width) * 2 - 1;
    mouse.y = -((event.clientY - rect.top) / rect.height) * 2 + 1;

    raycaster.setFromCamera(mouse, camera);
    const intersects = raycaster.intersectObjects(nodeMeshes, true);

    if (intersects.length > 0) {
        const obj = intersects[0].object.parent; 
        if (hoveredNode !== obj) {
            hoveredNode = obj; 
            updateHighlights();
            
            clearLabels();
            const el = createLabel(obj.userData.name);
            el.style.display = "block";
            el.style.border = "1px solid var(--accent)";
            el.style.color = "var(--text-main)";
            activeLabels.push({ el, pos: obj.position });

            container.style.cursor = "crosshair";
            controls.autoRotate = false;
        }
    } else {
        if (hoveredNode) { 
            hoveredNode = null; 
            updateHighlights(); 
            clearLabels();
            container.style.cursor = "default"; 
            controls.autoRotate = true; 
        }
    }
}

function onClick3D(e) { 
    if(tab !== "map") return;
    
    const container = document.getElementById("scene-container");
    const rect = container.getBoundingClientRect();
    mouse.x = ((e.clientX - rect.left) / rect.width) * 2 - 1;
    mouse.y = -((e.clientY - rect.top) / rect.height) * 2 + 1;

    raycaster.setFromCamera(mouse, camera);
    const intersects = raycaster.intersectObjects(nodeMeshes, true);
    
    if (intersects.length > 0) {
        const obj = intersects[0].object.parent; 
        selectedNodeId = obj.userData.id; 
        updateHighlights(); 
        if (e) e.stopPropagation();
        od(selectedNodeId); 
    } else {
        if (document.getElementById("drawer").contains(e.target)) return;
        selectedNodeId = null; 
        cd();
        updateHighlights(); 
    } 
}

function onWindowResize3D() {
    if(tab !== "map" || !camera || !renderer) return;
    const wrap = document.getElementById("map-view");
    const width = wrap.clientWidth;
    const height = wrap.clientHeight;
    camera.aspect = width / height;
    camera.updateProjectionMatrix();
    renderer.setSize(width, height);
}
'''

start_idx = content.find('function init3D() {')
end_idx = content.find('async function od(id){')

if start_idx != -1 and end_idx != -1:
    content = content[:start_idx] + new_code + content[end_idx:]
    with open(path, 'w', encoding='utf-8') as f:
        f.write(content)
    print('Template successfully updated')
else:
    print('Error: Could not find block')
