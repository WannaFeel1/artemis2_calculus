import math
import json
import webbrowser
import os

# ==========================================
# 1. 3D Kinematic & Parametric Engine (Artemis II Data)
# ==========================================
D_moon = 384.4       
omega_moon = 0.00266
tilt = 0.087 # ความเอียงวงโคจรดวงจันทร์ (Inclination) ~5 องศา

ship_data = []
moon_data = []
stagesData = []
path_colors = [] 

arc_length = 0.0
time = 0.0

def get_bezier_point_3d(t, p0, p1, p2, p3):
    u = 1 - t
    w1 = u**3
    w2 = 3 * u**2 * t
    w3 = 3 * u * t**2
    w4 = t**3
    x = w1*p0[0] + w2*p1[0] + w3*p2[0] + w4*p3[0]
    y = w1*p0[1] + w2*p1[1] + w3*p2[1] + w4*p3[1]
    z = w1*p0[2] + w2*p1[2] + w3*p2[2] + w4*p3[2]
    return x, y, z

def record_frame(x, y, z, stage_name, color):
    global arc_length, time
    
    vx, vy, vz, ax, ay, az = 0, 0, 0, 0, 0, 0
    if len(ship_data) > 0:
        prev = ship_data[-1]
        dx, dy, dz = x - prev["x"], y - prev["y"], z - prev["z"]
        arc_length += math.sqrt(dx**2 + dy**2 + dz**2)
        vx, vy, vz = dx / 0.1, dy / 0.1, dz / 0.1
        
        if len(ship_data) > 1:
            ax = (vx - prev["vx"]) / 0.1
            ay = (vy - prev["vy"]) / 0.1
            az = (vz - prev["vz"]) / 0.1

    mx = D_moon * math.cos(omega_moon * time)
    my = D_moon * math.sin(omega_moon * time) * math.cos(tilt)
    mz = D_moon * math.sin(omega_moon * time) * math.sin(tilt)
    
    ship_data.append({
        "x": round(x, 4), "y": round(y, 4), "z": round(z, 4),
        "vx": round(vx, 4), "vy": round(vy, 4), "vz": round(vz, 4),
        "ax": round(ax, 6), "ay": round(ay, 6), "az": round(az, 6),
        "arc": int(arc_length * 1000)
    })
    moon_data.append({"x": round(mx, 4), "y": round(my, 4), "z": round(mz, 4)})
    stagesData.append(stage_name)
    path_colors.append(color)
    time += 0.1

# --- Phase 1: LEO (Launch & Low Earth Orbit) ---
for i in range(100):
    th = math.pi + (i/100) * (2*math.pi)
    record_frame(6.8 * math.cos(th), 6.8 * math.sin(th) * math.cos(tilt), 6.8 * math.sin(th) * math.sin(tilt), "1. 發射與近地軌道 / LEO Checkout", "green")

# --- Phase 2: HEO (High Earth Orbit ~ 24 Hrs Demo) ---
for i in range(150):
    th = math.pi + (i/150) * (2*math.pi)
    r = (20 * (1 - 0.65**2)) / (1 - 0.65 * math.cos(th)) # HEO Orbit
    record_frame(r * math.cos(th), r * math.sin(th) * math.cos(tilt), r * math.sin(th) * math.sin(tilt), "2. 遠地點提升 / Apogee Raise (HEO)", "green")

# --- Phase 3: Outbound Transit (TLI to Moon) ---
tli_steps = 800
last = ship_data[-1]
for i in range(tli_steps):
    t = i / tli_steps
    ft = time + (tli_steps - i)*0.1
    tmx = D_moon * math.cos(omega_moon * ft)
    tmy = D_moon * math.sin(omega_moon * ft) * math.cos(tilt)
    tmz = D_moon * math.sin(omega_moon * ft) * math.sin(tilt)
    p0 = (last["x"], last["y"], last["z"])
    p1 = (100, -150, 10); p2 = (300, -50, -10); p3 = (tmx + 10.4, tmy - 10.4, tmz + 5) # Lunar approach
    x, y, z = get_bezier_point_3d(t, p0, p1, p2, p3)
    record_frame(x, y, z, "3. 地月轉移 / TLI & Outbound Transit", "green")

# --- Phase 4: Lunar Flyby (Artemis II Far Side Flyby ~10,427 km) ---
flyby_steps = 150
for i in range(flyby_steps):
    t = i / flyby_steps
    mx = D_moon * math.cos(omega_moon * time)
    my = D_moon * math.sin(omega_moon * time) * math.cos(tilt)
    mz = D_moon * math.sin(omega_moon * time) * math.sin(tilt)
    a = -math.pi/4 + (t * math.pi)
    r = 10.4 - (math.sin(t * math.pi) * 3) # Adjusted closest approach (Approx 10,400 km)
    record_frame(mx + r*math.cos(a), my + r*math.sin(a)*math.cos(tilt), mz + r*math.sin(a)*math.sin(tilt), "4. 繞月飛行 (月球背面) / Lunar Flyby", "blue")

# --- Phase 5: Return (Trans-Earth Return) ---
return_steps = 800
last = ship_data[-1]
for i in range(return_steps):
    t = i / return_steps
    p0 = (last["x"], last["y"], last["z"])
    p1 = (250, 180, -15); p2 = (50, 80, 5); p3 = (-6.8, 0, 0)
    x, y, z = get_bezier_point_3d(t, p0, p1, p2, p3)
    record_frame(x, y, z, "5. 返回地球 / Trans-Earth Return", "blue")

# --- Phase 6: Splashdown ---
for i in range(15): record_frame(-6.8, 0, 0, "6. 濺落與回收 / Splashdown", "blue")

# ==========================================
# 2. Web Engine & HTML (Calculus Educational Simulator)
# ==========================================
html_content = f"""<!DOCTYPE html>
<html lang="zh-TW">
<head>
    <meta charset="UTF-8">
    <title>NASA Artemis II - Physics & Calculus Simulator</title>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/three@0.128.0/examples/js/controls/OrbitControls.js"></script>
    <style>
        body {{ margin: 0; overflow: hidden; background: #000; font-family: 'Consolas', monospace; color: #fff; }}
        
        /* HUD */
        #hud {{ position: absolute; top: 20px; left: 20px; z-index: 10; pointer-events: none; }}
        h1 {{ margin: 0; font-size: 24px; display: flex; align-items: center; gap: 10px; text-shadow: 0 2px 5px rgba(0,0,0,0.8); }}
        .nasa-logo {{ background: #0b3d91; padding: 4px 8px; border-radius: 50%; font-weight: bold; font-family: Arial; font-size: 16px; }}
        #mission-time {{ font-size: 20px; color: #ff9900; font-weight: bold; margin-top: 10px; letter-spacing: 2px; text-shadow: 0 0 10px rgba(255,153,0,0.5); }}
        #lbl-stage {{ color: #00ff00; font-size: 14px; background: rgba(0,255,0,0.1); padding: 6px 12px; border-radius: 6px; display: inline-block; margin-top: 8px; border: 1px solid #00ff00; backdrop-filter: blur(5px); }}
        
        /* Camera Controls */
        #cam-controls {{ position: absolute; bottom: 20px; left: 50%; transform: translateX(-50%); z-index: 20; display: flex; gap: 8px; background: rgba(10,15,25,0.8); padding: 8px; border-radius: 8px; border: 1px solid #334; backdrop-filter: blur(5px); }}
        .cam-btn {{ background: rgba(26, 115, 232, 0.2); color: #8ab4f8; border: 1px solid transparent; padding: 10px 15px; cursor: pointer; border-radius: 6px; font-weight: bold; transition: 0.3s; font-family: 'Consolas'; }}
        .cam-btn:hover {{ background: rgba(26, 115, 232, 0.4); }}
        .cam-btn.active {{ background: #1a73e8; color: #fff; border-color: #4285f4; box-shadow: 0 0 10px rgba(26,115,232,0.5); }}
        
        /* Side Panel Toggle */
        #panel-toggle {{ position: absolute; top: 20px; right: 20px; z-index: 30; background: #1a73e8; color: white; border: none; padding: 8px 12px; border-radius: 6px; font-weight: bold; cursor: pointer; font-family: Consolas; transition: 0.3s; }}
        #panel-toggle:hover {{ background: #1557b0; }}
        
        /* Side Panel (HUD Math) */
        .panel {{ position: absolute; top: 60px; right: 20px; width: 380px; background: rgba(10, 15, 25, 0.85); border: 1px solid #334; border-radius: 12px; padding: 20px; backdrop-filter: blur(8px); border-top: 4px solid #00e5ff; z-index: 10; box-shadow: 0 5px 20px rgba(0,0,0,0.5); transition: 0.3s; transform-origin: top right; }}
        .panel.hidden {{ transform: scale(0.9); opacity: 0; pointer-events: none; }}
        
        .math-section {{ margin-bottom: 15px; border-bottom: 1px solid #223; padding-bottom: 10px; }}
        .math-title {{ font-size: 14px; color: #bbb; margin-bottom: 6px; font-weight: bold; }}
        .math-formula {{ font-size: 13px; color: #8ab4f8; margin-bottom: 6px; }}
        .math-live-sub {{ font-size: 13px; color: #ddd; background: rgba(0,0,0,0.6); padding: 8px; border-radius: 6px; border-left: 3px solid #ff9900; line-height: 1.4; }}
        .math-result {{ font-size: 20px; color: #00e5ff; font-weight: bold; margin-top: 6px; }}
        
        /* Bottom Left Buttons */
        .btn-container {{ position: absolute; bottom: 20px; left: 20px; z-index: 20; display: flex; gap: 10px; flex-direction: column; }}
        .btn {{ background: rgba(26, 115, 232, 0.2); color: #8ab4f8; border: 1px solid #1a73e8; padding: 12px 20px; border-radius: 8px; cursor: pointer; font-weight: bold; transition: 0.3s; backdrop-filter: blur(5px); text-align: left; font-family: 'Consolas'; }}
        .btn:hover {{ background: rgba(26, 115, 232, 0.6); color: white; }}
        .btn-replay {{ border-color: #ff9900; color: #ff9900; background: rgba(255, 153, 0, 0.1); }}
        
        /* Educational Math & Physics Modal */
        #desmos-modal {{ display: none; position: absolute; top: 50%; left: 50%; transform: translate(-50%, -50%); width: 95vw; height: 90vh; max-width: 1400px; background: rgba(10, 12, 18, 0.95); border: 1px solid #334; border-radius: 12px; z-index: 100; box-shadow: 0 10px 50px rgba(0,0,0,0.9); flex-direction: row; overflow: hidden; }}
        .desmos-sidebar {{ width: 40%; padding: 20px; border-right: 1px solid #223; background: rgba(0,0,0,0.3); overflow-y: auto; }}
        .desmos-canvas-container {{ width: 60%; position: relative; background: #050505; display: flex; flex-direction: column; }}
        
        /* UX/UI FIX: Toolbar inside Canvas Container to avoid overlaps */
        .modal-toolbar {{ display: flex; align-items: center; background: #111; border-bottom: 1px solid #333; padding-right: 15px; flex-shrink: 0; z-index: 2; height: 50px; }}
        .graph-tabs {{ display: flex; flex-grow: 1; height: 100%; }}
        .g-tab {{ flex: 1; padding: 15px; text-align: center; cursor: pointer; color: #888; background: #0a0a0a; border-right: 1px solid #222; font-weight: bold; transition: 0.2s; user-select: none; display: flex; align-items: center; justify-content: center; }}
        .g-tab:hover {{ background: #151515; }}
        .g-tab.active {{ color: #00e5ff; background: #1a1a1a; box-shadow: inset 0 -3px 0 #00e5ff; }}
        
        .btn-fullscreen {{ background: rgba(255,255,255,0.1); color: #fff; border: 1px solid #555; padding: 6px 12px; border-radius: 4px; cursor: pointer; font-size: 13px; margin-left: auto; transition: 0.3s; font-family: 'Consolas'; }}
        .btn-fullscreen:hover {{ background: #1a73e8; border-color: #1a73e8; }}
        .modal-close {{ background: rgba(255,0,0,0.2); border: 1px solid #ff5555; color: #fff; font-size: 16px; cursor: pointer; z-index: 101; width: 30px; height: 30px; border-radius: 50%; display: flex; align-items: center; justify-content: center; margin-left: 15px; transition: 0.2s; }}
        .modal-close:hover {{ background: #ff5555; }}
        
        .graph-content-area {{ flex-grow: 1; position: relative; width: 100%; }}
        #desmos-grid {{ position: absolute; top: 0; left: 0; width: 100%; height: 100%; display: block; }}
        #graph-3d-container {{ position: absolute; top: 0; left: 0; width: 100%; height: 100%; display: none; }}
        
        /* Overlays */
        #ship-label-3d {{ position: absolute; top: 15px; left: 15px; color: #00e5ff; background: rgba(0,0,0,0.7); padding: 8px 12px; border-radius: 6px; border-left: 3px solid #00e5ff; font-size: 14px; z-index: 10; display: none; pointer-events: none; }}
        #axes-legend-3d {{ position: absolute; bottom: 15px; right: 15px; background: rgba(0,0,0,0.7); padding: 10px; border-radius: 6px; border: 1px solid #334; font-size: 12px; display: none; pointer-events: none; }}
        
        .eq-box {{ background: rgba(20,25,35,0.8); border-left: 4px solid #1a73e8; padding: 12px; margin-bottom: 12px; border-radius: 4px; font-size: 13px; color: #ccc; }}
        .eq-hl {{ color: #fff; font-family: monospace; background: #000; padding: 6px; border-radius: 3px; display: block; margin-top: 6px; font-size: 13px; border: 1px solid #333; }}
        
        .desmos-sidebar::-webkit-scrollbar {{ width: 8px; }}
        .desmos-sidebar::-webkit-scrollbar-track {{ background: rgba(0,0,0,0.1); }}
        .desmos-sidebar::-webkit-scrollbar-thumb {{ background: #334; border-radius: 4px; }}
    </style>
</head>
<body>
    <div id="hud">
        <h1><span class="nasa-logo">NASA</span> ARTEMIS II</h1>
        <div id="mission-time">MET: T+ 00:00:00:00</div>
        <div id="lbl-stage">SYSTEM CHECKOUT</div>
    </div>

    <div id="cam-controls">
        <button class="cam-btn active" id="btn-cam-free" onclick="setCamera('free')">🎥 自由視角 / Free Cam</button>
        <button class="cam-btn" id="btn-cam-ship" onclick="setCamera('ship')">🚀 太空船視角 / Ship POV</button>
        <button class="cam-btn" id="btn-cam-moon" onclick="setCamera('moon')">🌕 月球視角 / Moon POV</button>
    </div>

    <!-- Toggle HUD Math Button -->
    <button id="panel-toggle" onclick="toggleMainPanel()">[ - ] Hide Math Panel</button>

    <!-- Live Math Panel (Main View) -->
    <div id="live-math-panel" class="panel">
        <div class="math-section">
            <div class="math-title">1. 3D 距離向量 / 3D Distance Vector</div>
            <div class="math-formula">|r| = &radic;(x&sup2; + y&sup2; + z&sup2;)</div>
            <div class="math-live-sub" id="sub-dist">Calculating...</div>
            <div class="math-result" id="res-dist">0 km</div>
        </div>
        <div class="math-section">
            <div class="math-title">2. 3D 速度向量 / 3D Velocity Mag.</div>
            <div class="math-formula">|v| = &radic;(vx&sup2; + vy&sup2; + vz&sup2;)</div>
            <div class="math-live-sub" id="sub-vel">Calculating...</div>
            <div class="math-result" id="res-vel">0 km/s</div>
        </div>
        <div class="math-section" style="border-bottom:none;">
            <div class="math-title">3. 動力學狀態 / Dynamic State</div>
            <div class="math-live-sub" id="sub-acc">a: 0.00 m/s&sup2;<br>L: 0 km</div>
        </div>
    </div>
    
    <div class="btn-container">
        <button class="btn" onclick="toggleDesmos()">📈 微積分與物理教學圖表 / Calculus & Math Modal</button>
        <button class="btn btn-replay" onclick="replayMission()">↺ 重新播放 / Replay Mission</button>
    </div>

    <!-- Educational Calculus & Math Modal -->
    <div id="desmos-modal">
        <div class="desmos-sidebar">
            
            <h3 style="color:#00e5ff; margin-top:0; border-bottom: 1px solid #334; padding-bottom: 8px;">太空船基礎微積分 / Basic Calculus</h3>
            
            <div class="eq-box" style="border-color:#1a73e8;">
                <b>1. 3D 位置向量 (3D Position Vector)</b><br>
                r(t) = xi + yj + zk<br>
                |r| = &radic;(x&sup2; + y&sup2; + z&sup2;) (畢氏定理)<br>
                <span class="eq-hl" id="calc-pos">Calculating...</span>
            </div>
            
            <div class="eq-box" style="border-color:#00ff00;">
                <b>2. 3D 速度微積分 (Velocity Derivative)</b><br>
                v(t) = r'(t) = (dx/dt)i + (dy/dt)j + (dz/dt)k<br>
                |v| = &radic;(vx&sup2; + vy&sup2; + vz&sup2;)<br>
                <span class="eq-hl" id="calc-vel">Calculating...</span>
            </div>

            <div class="eq-box" style="border-color:#ffff00;">
                <b>3. 動力學狀態 (Dynamic State)</b><br>
                a = v'(t) (加速度) | L = &int; |v| dt (弧長)<br>
                <span class="eq-hl" id="calc-acc">Calculating...</span>
            </div>

            <h3 style="color:#ff9900; margin-top:20px; border-bottom: 1px solid #334; padding-bottom: 8px;">月球軌道與相對距離 / Lunar Distances</h3>
            
            <div class="eq-box" style="border-color:#ff9900;">
                <b>月球運動學 (Moon Kinematics)</b><br>
                R_m = 384,400 km | &omega; = 0.00266 rad/s<br>
                r_m(t) = Rcos(&omega;t)i + Rsin(&omega;t)cos(i)j + Rsin(&omega;t)sin(i)k<br>
                <span class="eq-hl" id="calc-moon">Calculating...</span>
            </div>

            <div class="eq-box" style="border-color:#ff00ff;">
                <b>相對距離 (Relative Distances)</b><br>
                <span class="eq-hl" id="calc-dist">Calculating...</span>
            </div>

            <h3 style="color:#ff5555; margin-top:20px; border-bottom: 1px solid #334; padding-bottom: 8px;">高階軌道微積分 / Advanced Vector Calculus</h3>
            
            <div class="eq-box" style="border-color:#ff5555;">
                <b>切線與法線加速度 (Tangential & Normal Accel)</b><br>
                a_T = (v &middot; a) / |v| (加速/減速)<br>
                a_N = &radic;(|a|&sup2; - a_T&sup2;) (改變方向)<br>
                <span class="eq-hl" id="calc-curv">Calculating...</span>
            </div>
            
            <div class="eq-box" style="border-color:#ff5555;">
                <b>特定軌道能 (Vis-viva Integral)</b><br>
                &epsilon; = v&sup2;/2 - &mu;/r<br>
                <span class="eq-hl" id="calc-eng">Calculating...</span>
            </div>
        </div>
        
        <div class="desmos-canvas-container">
            <!-- UX/UI FIXED: Toolbar to prevent overlap -->
            <div class="modal-toolbar">
                <div class="graph-tabs">
                    <div class="g-tab active" id="tab-2d" onclick="setGraphMode('2D')">2D Graph (X-Y)</div>
                    <div class="g-tab" id="tab-3d" onclick="setGraphMode('3D')">3D Graph (X-Y-Z)</div>
                </div>
                <button class="btn-fullscreen" onclick="toggleFullscreenGraph()">⛶ 全螢幕 (Fullscreen)</button>
                <button class="modal-close" onclick="toggleDesmos()">×</button>
            </div>
            
            <div class="graph-content-area" id="graph-content-area">
                <canvas id="desmos-grid"></canvas>
                <div id="graph-3d-container">
                    <div id="ship-label-3d">Ship (x: 0, y: 0, z: 0)</div>
                    <div id="axes-legend-3d">
                        <b>3D 座標軸 (Axes)</b><br>
                        <span style="color:#ff5555; font-weight:bold;">&rarr;</span> X 軸 (Red)<br>
                        <span style="color:#00ff00; font-weight:bold;">&uarr;</span> Y 軸 (Green)<br>
                        <span style="color:#00aaff; font-weight:bold;">&nearr;</span> Z 軸 (Blue)
                    </div>
                </div>
            </div>
        </div>
    </div>

    <script>
        const shipData = {json.dumps(ship_data)};
        const moonData = {json.dumps(moon_data)};
        const stagesData = {json.dumps(stagesData)};
        const pathColors = {json.dumps(path_colors)};
        const MAX = shipData.length;

        // --- MAIN 3D Scene ---
        const scene = new THREE.Scene();
        const camera = new THREE.PerspectiveCamera(45, window.innerWidth/window.innerHeight, 0.1, 5000);
        camera.position.set(200, -200, 500);
        const renderer = new THREE.WebGLRenderer({{ antialias: true, logarithmicDepthBuffer: true }});
        renderer.setSize(window.innerWidth, window.innerHeight);
        document.body.appendChild(renderer.domElement);
        const controls = new THREE.OrbitControls(camera, renderer.domElement);
        controls.enableDamping = true;

        scene.add(new THREE.AmbientLight(0x333333));
        const sunLight = new THREE.PointLight(0xffffff, 2.5, 3000);
        sunLight.position.set(500, 300, 150); scene.add(sunLight);

        const starGeo = new THREE.BufferGeometry();
        const starPts = new Float32Array(3000);
        for(let i=0; i<3000; i++) starPts[i] = (Math.random()-0.5)*2000;
        starGeo.setAttribute('position', new THREE.BufferAttribute(starPts, 3));
        scene.add(new THREE.Points(starGeo, new THREE.PointsMaterial({{color: 0xffffff, size: 1.2}})));

        const earth = new THREE.Mesh(new THREE.SphereGeometry(6.371, 64, 64), new THREE.MeshPhongMaterial({{map: new THREE.TextureLoader().load('https://raw.githubusercontent.com/mrdoob/three.js/master/examples/textures/planets/earth_atmos_2048.jpg')}}));
        scene.add(earth);

        const moon = new THREE.Mesh(new THREE.SphereGeometry(6.0, 64, 64), new THREE.MeshPhongMaterial({{map: new THREE.TextureLoader().load('https://raw.githubusercontent.com/mrdoob/three.js/master/examples/textures/planets/moon_1024.jpg'), emissive: 0x111111}}));
        scene.add(moon);
        
        const orbitGeo = new THREE.BufferGeometry();
        const oPts = [];
        for(let i=0; i<=100; i++) {{
            let a = (i/100) * Math.PI * 2;
            oPts.push(new THREE.Vector3(384.4 * Math.cos(a), 384.4 * Math.sin(a) * Math.cos(0.087), 384.4 * Math.sin(a) * Math.sin(0.087)));
        }}
        orbitGeo.setFromPoints(oPts);
        scene.add(new THREE.Line(orbitGeo, new THREE.LineBasicMaterial({{color: 0x444444, transparent: true, opacity: 0.6}})));

        const shipGroup = new THREE.Group();
        const cm = new THREE.Mesh(new THREE.ConeGeometry(1.5, 3, 16), new THREE.MeshPhongMaterial({{color: 0xffffff}}));
        cm.rotation.x = Math.PI/2; shipGroup.add(cm);
        scene.add(shipGroup);

        const lineGeoOut = new THREE.BufferGeometry();
        const lineGeoIn = new THREE.BufferGeometry();
        const posOut = new Float32Array(MAX * 3);
        const posIn = new Float32Array(MAX * 3);
        lineGeoOut.setAttribute('position', new THREE.BufferAttribute(posOut, 3));
        lineGeoIn.setAttribute('position', new THREE.BufferAttribute(posIn, 3));
        scene.add(new THREE.Line(lineGeoOut, new THREE.LineBasicMaterial({{color: 0x00ff00}})));
        scene.add(new THREE.Line(lineGeoIn, new THREE.LineBasicMaterial({{color: 0x00aaff}})));

        // --- SUB 3D Scene (For Modal Interactive Graph) ---
        const subContainer = document.getElementById('graph-3d-container');
        const subScene = new THREE.Scene();
        const subCamera = new THREE.PerspectiveCamera(50, 1, 0.1, 2000);
        subCamera.position.set(200, 200, 300); 
        
        const subRenderer = new THREE.WebGLRenderer({{ alpha: true, antialias: true }});
        subContainer.appendChild(subRenderer.domElement);
        
        const subControls = new THREE.OrbitControls(subCamera, subRenderer.domElement);
        subControls.enableDamping = true;
        
        // 3D Reference Objects
        subScene.add(new THREE.AxesHelper(150)); 
        subScene.add(new THREE.GridHelper(800, 40, 0x444444, 0x222222));
        const subEarth = new THREE.Mesh(new THREE.SphereGeometry(10,32,32), new THREE.MeshBasicMaterial({{color: 0x1a73e8}})); subScene.add(subEarth);
        const subMoon = new THREE.Mesh(new THREE.SphereGeometry(5,32,32), new THREE.MeshBasicMaterial({{color: 0xaaaaaa}})); subScene.add(subMoon);
        const subShip = new THREE.Mesh(new THREE.SphereGeometry(3,16,16), new THREE.MeshBasicMaterial({{color: 0xffffff}})); subScene.add(subShip);
        
        subScene.add(new THREE.Line(lineGeoOut, new THREE.LineBasicMaterial({{color: 0x00ff00}})));
        subScene.add(new THREE.Line(lineGeoIn, new THREE.LineBasicMaterial({{color: 0x00aaff}})));
        subScene.add(new THREE.Line(orbitGeo, new THREE.LineBasicMaterial({{color: 0x444444}})));

        const velArrow = new THREE.ArrowHelper(new THREE.Vector3(1,0,0), new THREE.Vector3(0,0,0), 20, 0x00e5ff, 15, 10); subScene.add(velArrow);
        const accArrow = new THREE.ArrowHelper(new THREE.Vector3(1,0,0), new THREE.Vector3(0,0,0), 20, 0xff5555, 15, 10); subScene.add(accArrow);

        // --- Logic Variables ---
        let globalFrame = 0; 
        let shipFrame = 0;
        let outC = 0, inC = 0;
        let isDesmos = false, gMode = '2D', camMode = 'free';
        const ctx2d = document.getElementById('desmos-grid').getContext('2d');

        function toggleMainPanel() {{
            const p = document.getElementById('live-math-panel');
            const btn = document.getElementById('panel-toggle');
            p.classList.toggle('hidden');
            if (p.classList.contains('hidden')) {{
                btn.innerText = '[ + ] Show Math Panel';
            }} else {{
                btn.innerText = '[ - ] Hide Math Panel';
            }}
        }}

        function toggleFullscreenGraph() {{
            const container = document.getElementById('graph-content-area');
            if (!document.fullscreenElement) {{
                container.requestFullscreen().catch(err => alert("Fullscreen error: " + err.message));
            }} else {{
                document.exitFullscreen();
            }}
        }}

        document.addEventListener('fullscreenchange', () => {{
            if(isDesmos) {{
                setTimeout(() => {{
                    const area = document.getElementById('graph-content-area');
                    if(gMode === '2D') {{
                        const c2d = document.getElementById('desmos-grid');
                        c2d.width = area.clientWidth; c2d.height = area.clientHeight;
                    }} else {{
                        subRenderer.setSize(area.clientWidth, area.clientHeight);
                        subCamera.aspect = area.clientWidth / area.clientHeight;
                        subCamera.updateProjectionMatrix();
                    }}
                }}, 150); // Delay for browser layout update
            }}
        }});

        function toggleDesmos() {{ 
            isDesmos = !isDesmos; 
            const modal = document.getElementById('desmos-modal');
            modal.style.display = isDesmos ? 'flex' : 'none'; 
            
            if(isDesmos) {{
                const area = document.getElementById('graph-content-area');
                const c2d = document.getElementById('desmos-grid');
                c2d.width = area.clientWidth; c2d.height = area.clientHeight;
                subRenderer.setSize(area.clientWidth, area.clientHeight);
                subCamera.aspect = area.clientWidth / area.clientHeight;
                subCamera.updateProjectionMatrix();
            }}
        }}
        
        function setGraphMode(m) {{ 
            gMode = m; 
            document.getElementById('tab-2d').className = 'g-tab' + (m==='2D'?' active':''); 
            document.getElementById('tab-3d').className = 'g-tab' + (m==='3D'?' active':''); 
            
            document.getElementById('desmos-grid').style.display = m==='2D' ? 'block' : 'none';
            document.getElementById('graph-3d-container').style.display = m==='3D' ? 'block' : 'none';
            document.getElementById('ship-label-3d').style.display = m==='3D' ? 'block' : 'none';
            document.getElementById('axes-legend-3d').style.display = m==='3D' ? 'block' : 'none';
            
            if(m === '3D') {{
                const area = document.getElementById('graph-content-area');
                subRenderer.setSize(area.clientWidth, area.clientHeight);
                subCamera.aspect = area.clientWidth / area.clientHeight;
                subCamera.updateProjectionMatrix();
            }}
        }}
        
        function setCamera(m) {{ 
            camMode = m; 
            document.getElementById('btn-cam-free').className = 'cam-btn' + (m==='free'?' active':'');
            document.getElementById('btn-cam-ship').className = 'cam-btn' + (m==='ship'?' active':'');
            document.getElementById('btn-cam-moon').className = 'cam-btn' + (m==='moon'?' active':'');
        }}
        
        window.replayMission = function() {{ 
            shipFrame = outC = inC = 0; 
            globalFrame = 0;
            lineGeoOut.setDrawRange(0,0); lineGeoIn.setDrawRange(0,0); 
            shipGroup.visible = true; 
            setCamera('free'); 
        }};

        function getMET(f) {{
            let ts = Math.floor(f * (864000 / MAX));
            let d = Math.floor(ts/86400); ts %= 86400;
            let h = Math.floor(ts/3600); ts %= 3600;
            let m = Math.floor(ts/60); let s = ts%60;
            return 'MET: T+ ' + String(d).padStart(2,'0') + ':' + String(h).padStart(2,'0') + ':' + String(m).padStart(2,'0') + ':' + String(s).padStart(2,'0');
        }}

        const camTargetPos = new THREE.Vector3();
        const camLookTarget = new THREE.Vector3();

        function updateCalculusHTML(s, mx, my, mz) {{
            const v2 = s.vx*s.vx + s.vy*s.vy + s.vz*s.vz;
            const r = Math.sqrt(s.x*s.x + s.y*s.y + s.z*s.z);
            const mDist = Math.sqrt(mx*mx + my*my + mz*mz);
            const accMag = Math.sqrt(s.ax*s.ax + s.ay*s.ay + s.az*s.az);
            
            // Distances
            const dSE = r; 
            const dSM = Math.sqrt(Math.pow(mx-s.x,2) + Math.pow(my-s.y,2) + Math.pow(mz-s.z,2)); 
            
            // Basic Calculus
            document.getElementById('calc-pos').innerHTML = 'r = ('+s.x.toFixed(1)+')i + ('+s.y.toFixed(1)+')j + ('+s.z.toFixed(1)+')k<br>|r| = &radic;( ('+s.x.toFixed(1)+')&sup2; + ('+s.y.toFixed(1)+')&sup2; + ('+s.z.toFixed(1)+')&sup2; )<br>= '+Math.round(r*1000).toLocaleString()+' km';
            document.getElementById('calc-vel').innerHTML = 'v = ('+s.vx.toFixed(2)+')i + ('+s.vy.toFixed(2)+')j + ('+s.vz.toFixed(2)+')k<br>|v| = &radic;( ('+s.vx.toFixed(2)+')&sup2; + ('+s.vy.toFixed(2)+')&sup2; + ('+s.vz.toFixed(2)+')&sup2; )<br>= '+Math.sqrt(v2).toFixed(2)+' km/s';
            document.getElementById('calc-acc').innerHTML = 'a: ' + (accMag*100).toFixed(4) + ' m/s&sup2;<br>L: ' + s.arc.toLocaleString() + ' km';

            // Moon Calculus
            const vMoon = 384.4 * 0.00266; 
            document.getElementById('calc-moon').innerHTML = 'r_m = ('+mx.toFixed(1)+')i + ('+my.toFixed(1)+')j + ('+mz.toFixed(1)+')k<br>v_m = '+vMoon.toFixed(2)+' km/s';
            document.getElementById('calc-dist').innerHTML = '地球-月球 (Earth-Moon): '+Math.round(mDist*1000).toLocaleString()+' km<br>地球-太空船 (Earth-Ship): '+Math.round(dSE*1000).toLocaleString()+' km<br>月球-太空船 (Moon-Ship): <span style="color:#ff5555;">'+Math.round(dSM*1000).toLocaleString()+' km</span>';

            // Advanced Calculus: Tangential & Normal Acceleration
            const vDotA = s.vx*s.ax + s.vy*s.ay + s.vz*s.az;
            const aT = (Math.sqrt(v2) > 0) ? (vDotA / Math.sqrt(v2)) : 0;
            const aN = Math.sqrt(Math.max(0, accMag*accMag - aT*aT));
            
            const eng = (v2 / 2) - (398.6 / r);
            
            document.getElementById('calc-curv').innerHTML = 'a_T = ' + (aT*100).toFixed(4) + ' m/s&sup2; (Speed change)<br>a_N = ' + (aN*100).toFixed(4) + ' m/s&sup2; (Direction change)';
            document.getElementById('calc-eng').innerHTML = '&epsilon; = ('+Math.sqrt(v2).toFixed(2)+')&sup2;/2 - 398.6/'+r.toFixed(1)+'<br>= ' + eng.toFixed(4) + ' km&sup2;/s&sup2;';
        }}

        function animate() {{
            requestAnimationFrame(animate);
            earth.rotation.y += 0.005;
            
            const cTime = globalFrame * 0.1;
            const omega = 0.00266;
            const tiltR = 0.087;
            const currentMx = 384.4 * Math.cos(omega * cTime);
            const currentMy = 384.4 * Math.sin(omega * cTime) * Math.cos(tiltR);
            const currentMz = 384.4 * Math.sin(omega * cTime) * Math.sin(tiltR);
            moon.position.set(currentMx, currentMy, currentMz);
            
            document.getElementById('mission-time').innerText = getMET(globalFrame);
            globalFrame++;

            const activeS = shipData[Math.min(shipFrame, MAX - 1)];

            if (shipFrame < MAX) {{
                shipGroup.position.set(activeS.x, activeS.y, activeS.z);
                
                if (shipFrame < MAX - 1) {{
                    const ns = shipData[shipFrame+1];
                    shipGroup.lookAt(new THREE.Vector3(ns.x, ns.y, ns.z));
                }}
                
                if (pathColors[shipFrame] === "green") {{
                    posOut[outC*3]=activeS.x; posOut[outC*3+1]=activeS.y; posOut[outC*3+2]=activeS.z;
                    lineGeoOut.attributes.position.needsUpdate = true; lineGeoOut.setDrawRange(0, ++outC);
                }} else {{
                    posIn[inC*3]=activeS.x; posIn[inC*3+1]=activeS.y; posIn[inC*3+2]=activeS.z;
                    lineGeoIn.attributes.position.needsUpdate = true; lineGeoIn.setDrawRange(0, ++inC);
                }}

                if (shipFrame % 3 === 0) {{
                    document.getElementById('sub-dist').innerHTML = '&radic;( ('+activeS.x.toFixed(0)+')&sup2; + ('+activeS.y.toFixed(0)+')&sup2; + ('+activeS.z.toFixed(0)+')&sup2; )';
                    document.getElementById('res-dist').innerText = Math.round(Math.sqrt(activeS.x*activeS.x + activeS.y*activeS.y + activeS.z*activeS.z)*1000).toLocaleString() + ' km';
                    document.getElementById('sub-vel').innerHTML = '&radic;( ('+activeS.vx.toFixed(2)+')&sup2; + ('+activeS.vy.toFixed(2)+')&sup2; + ('+activeS.vz.toFixed(2)+')&sup2; )';
                    document.getElementById('res-vel').innerText = Math.sqrt(activeS.vx*activeS.vx + activeS.vy*activeS.vy + activeS.vz*activeS.vz).toFixed(2) + ' km/s';
                    
                    const accMag = Math.sqrt(activeS.ax*activeS.ax + activeS.ay*activeS.ay + activeS.az*activeS.az);
                    document.getElementById('sub-acc').innerHTML = 'a: ' + (accMag*100).toFixed(4) + ' m/s&sup2;<br>L: ' + activeS.arc.toLocaleString() + ' km';
                    document.getElementById('lbl-stage').innerText = stagesData[shipFrame];
                }}
                shipFrame++;
            }} else {{
                shipGroup.visible = false;
            }}

            if(camMode === 'ship' && shipGroup.visible) {{
                camTargetPos.set(activeS.x - activeS.vx*3, activeS.y - activeS.vy*3 + 10, activeS.z - activeS.vz*3);
                camLookTarget.set(activeS.x + activeS.vx*10, activeS.y + activeS.vy*10, activeS.z + activeS.vz*10);
                camera.position.lerp(camTargetPos, 0.1); 
                controls.target.lerp(camLookTarget, 0.1);
            }} else if(camMode === 'moon') {{
                camTargetPos.set(currentMx + 30, currentMy + 15, currentMz + 30);
                camera.position.lerp(camTargetPos, 0.05);
                controls.target.lerp(earth.position, 0.05);
            }} else if(camMode === 'ship' && !shipGroup.visible) {{
                setCamera('free'); 
            }}
            controls.update();

            if (isDesmos) {{
                updateCalculusHTML(activeS, currentMx, currentMy, currentMz);
                if (gMode === '2D') {{
                    const w = document.getElementById('desmos-grid').width;
                    const h = document.getElementById('desmos-grid').height;
                    const ox = w/2, oy = h/2; 
                    const sf = 0.65; 
                    
                    ctx2d.clearRect(0,0,w,h);
                    
                    // Draw Colored Axes
                    ctx2d.strokeStyle = '#222'; ctx2d.lineWidth = 1;
                    for(let i=0; i<w; i+=40) {{ ctx2d.beginPath(); ctx2d.moveTo(i,0); ctx2d.lineTo(i,h); ctx2d.stroke(); }}
                    for(let i=0; i<h; i+=40) {{ ctx2d.beginPath(); ctx2d.moveTo(0,i); ctx2d.lineTo(w,i); ctx2d.stroke(); }}
                    
                    ctx2d.lineWidth = 1.5;
                    ctx2d.strokeStyle = '#ff5555'; ctx2d.beginPath(); ctx2d.moveTo(0,oy); ctx2d.lineTo(w,oy); ctx2d.stroke(); // X Axis Red
                    ctx2d.strokeStyle = '#00ff00'; ctx2d.beginPath(); ctx2d.moveTo(ox,0); ctx2d.lineTo(ox,h); ctx2d.stroke(); // Y Axis Green
                    
                    ctx2d.fillStyle = '#ff5555'; ctx2d.font = 'bold 12px Consolas'; ctx2d.fillText('X 軸 (Axis)', w-70, oy-10);
                    ctx2d.fillStyle = '#00ff00'; ctx2d.fillText('Y 軸 (Axis)', ox+10, 20);
                    
                    ctx2d.fillStyle = '#1a73e8'; ctx2d.beginPath(); ctx2d.arc(ox, oy, 8, 0, 7); ctx2d.fill(); 
                    ctx2d.fillStyle = '#aaa'; ctx2d.beginPath(); ctx2d.arc(ox + currentMx*sf, oy - currentMy*sf, 5, 0, 7); ctx2d.fill(); 
                    
                    const px = ox + activeS.x*sf, py = oy - activeS.y*sf;
                    ctx2d.fillStyle = '#fff'; ctx2d.beginPath(); ctx2d.arc(px, py, 3, 0, 7); ctx2d.fill(); 
                    
                    ctx2d.strokeStyle = '#00e5ff'; ctx2d.lineWidth = 2; ctx2d.beginPath(); ctx2d.moveTo(px,py); ctx2d.lineTo(px + activeS.vx*5, py - activeS.vy*5); ctx2d.stroke();
                    ctx2d.strokeStyle = '#ff5555'; ctx2d.lineWidth = 2; ctx2d.beginPath(); ctx2d.moveTo(px,py); ctx2d.lineTo(px + activeS.ax*5000, py - activeS.ay*5000); ctx2d.stroke();
                    
                    ctx2d.fillStyle = '#fff'; ctx2d.font = '12px Consolas';
                    ctx2d.fillText('Ship(x:'+activeS.x.toFixed(0)+', y:'+activeS.y.toFixed(0)+')', px+10, py-10);
                }} else {{
                    subMoon.position.set(currentMx, currentMy, currentMz);
                    subShip.position.set(activeS.x, activeS.y, activeS.z);
                    
                    const vDir = new THREE.Vector3(activeS.vx, activeS.vy, activeS.vz);
                    if(vDir.length() > 0) {{
                        velArrow.setDirection(vDir.clone().normalize());
                        velArrow.setLength(vDir.length() * 10, 10, 5);
                        velArrow.position.copy(subShip.position);
                    }}
                    
                    const aDir = new THREE.Vector3(activeS.ax, activeS.ay, activeS.az);
                    if(aDir.length() > 0) {{
                        accArrow.setDirection(aDir.clone().normalize());
                        accArrow.setLength(aDir.length() * 10000, 10, 5);
                        accArrow.position.copy(subShip.position);
                    }}
                    
                    document.getElementById('ship-label-3d').innerText = 'Ship (x: ' + activeS.x.toFixed(1) + ', y: ' + activeS.y.toFixed(1) + ', z: ' + activeS.z.toFixed(1) + ')';
                }}
            }}
            
            renderer.render(scene, camera);
            if(isDesmos && gMode === '3D') {{
                subControls.update();
                subRenderer.render(subScene, subCamera);
            }}
        }}
        animate();
    </script>
</body>
</html>"""

filename = "artemis2_calculus_ultimate.html"
with open(filename, "w", encoding="utf-8") as f:
    f.write(html_content)

webbrowser.open('file://' + os.path.realpath(filename))
print("✅ Artemis II NASA Calculus Master Simulator with Fullscreen and Tangential Acceleration is Ready!")