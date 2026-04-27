import math
import json
import webbrowser
import os

# ==========================================
# 1. Kinematic & Parametric Engine
# ==========================================
D_moon = 384.4        
omega_moon = 0.00266

ship_data = []
moon_data = []
live_math = []
stagesData = []
path_colors = []

arc_length = 0.0
time = 0.0

def get_bezier_point(t, p0, p1, p2, p3):
    u = 1 - t
    w1 = u**3
    w2 = 3 * u**2 * t
    w3 = 3 * u * t**2
    w4 = t**3
    x = w1*p0[0] + w2*p1[0] + w3*p2[0] + w4*p3[0]
    y = w1*p0[1] + w2*p1[1] + w3*p2[1] + w4*p3[1]
    return x, y

def record_frame(x, y, stage_name, color):
    global arc_length, time
   
    vx, vy, ax, ay = 0, 0, 0, 0
    if len(ship_data) > 0:
        prev_x, prev_y = ship_data[-1]["x"], ship_data[-1]["y"]
        dx, dy = x - prev_x, y - prev_y
        arc_length += math.hypot(dx, dy)
        vx = dx / 0.1
        vy = dy / 0.1
        if len(ship_data) > 1:
            prev_vx, prev_vy = ship_data[-1]["vx"], ship_data[-1]["vy"]
            ax = (vx - prev_vx) / 0.1
            ay = (vy - prev_vy) / 0.1

    mx = D_moon * math.cos(omega_moon * time)
    my = D_moon * math.sin(omega_moon * time)
   
    dist_E = math.hypot(x, y)
    dist_M = math.hypot(x - mx, y - my)
   
    ship_data.append({"x": round(x, 4), "y": round(y, 4), "vx": round(vx, 4), "vy": round(vy, 4)})
    moon_data.append({"x": round(mx, 4), "y": round(my, 4)})
   
    live_math.append({
        "dist_E": int(dist_E * 1000),
        "dist_M": int(dist_M * 1000),
        "vel": round(math.hypot(vx, vy), 2),
        "acc": round(math.hypot(ax, ay), 4),
        "arc": int(arc_length * 1000)
    })
    stagesData.append(stage_name)
    path_colors.append(color)
    time += 0.1

# --- Phase 1: LEO ---
for i in range(100):
    theta = math.pi + (i/100) * (2*math.pi)
    record_frame(6.8 * math.cos(theta), 6.8 * math.sin(theta), "1-3: 發射與近地軌道檢查 / Launch & LEO Checkout", "green")

# --- Phase 2: HEO ---
for i in range(150):
    theta = math.pi + (i/150) * (2*math.pi)
    r = (18 * (1 - 0.62**2)) / (1 - 0.62 * math.cos(theta))
    record_frame(r * math.cos(theta), r * math.sin(theta), "4-6: 遠地點提升 / Apogee Raise Burn", "green")

# --- Phase 3: Outbound Transit ---
tli_steps = 800
# 【修正點】：動態獲取上一階段(HEO)的最後一個座標，做為飛向月球的起點
start_x, start_y = ship_data[-1]["x"], ship_data[-1]["y"]

for i in range(tli_steps):
    t = i / tli_steps
    future_time = time + (tli_steps - i)*0.1
    target_mx = D_moon * math.cos(omega_moon * future_time)
    target_my = D_moon * math.sin(omega_moon * future_time)
   
    p0 = (start_x, start_y) # 【修正點】：替換掉原本寫死的 (18, 0)
    p1 = (100, -150)
    p2 = (300, -50)
    p3 = (target_mx + 10, target_my - 15)
   
    x, y = get_bezier_point(t, p0, p1, p2, p3)
    record_frame(x, y, "7-10: 地月轉移與地月航行 / TLI & Outbound Transit", "green")

# --- Phase 4: Lunar Flyby ---
flyby_steps = 150
for i in range(flyby_steps):
    t = i / flyby_steps
    mx = D_moon * math.cos(omega_moon * time)
    my = D_moon * math.sin(omega_moon * time)
   
    angle = -math.pi/4 + (t * math.pi)
    radius = 15 - (math.sin(t * math.pi) * 5)
    record_frame(mx + radius*math.cos(angle), my + radius*math.sin(angle), "11: 繞月飛行 (月球背面) / Lunar Flyby (Far Side)", "blue")

# --- Phase 5: Trans-Earth Return ---
return_steps = 800
start_x_return, start_y_return = ship_data[-1]["x"], ship_data[-1]["y"]
for i in range(return_steps):
    t = i / return_steps
    p0 = (start_x_return, start_y_return)
    p1 = (250, 150)
    p2 = (50, 80)
    p3 = (-6.8, 0)
   
    x, y = get_bezier_point(t, p0, p1, p2, p3)
    record_frame(x, y, "12-14: 返回地球 / Trans-Earth Return", "blue")

# --- Phase 6: Splashdown ---
for i in range(50):
    record_frame(-6.8, 0, "15: 濺落與回收 / Splashdown & Recovery", "blue")

# ==========================================
# 2. Web Engine & HTML
# ==========================================
html_content = f"""<!DOCTYPE html>
<html lang="zh-TW">
<head>
    <meta charset="UTF-8">
    <title>NASA Artemis II - Authentic Figure-8 Route / 真實八字軌道</title>
    <script src="https://polyfill.io/v3/polyfill.min.js?features=es6"></script>
    <script id="MathJax-script" async src="https://cdn.jsdelivr.net/npm/mathjax@3/es5/tex-mml-chtml.js"></script>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/three@0.128.0/examples/js/controls/OrbitControls.js"></script>
    <style>
        body {{ margin: 0; overflow: hidden; background: #000; font-family: 'Consolas', monospace; color: #fff; }}
        #hud {{ position: absolute; top: 20px; left: 20px; z-index: 10; pointer-events: none; }}
        h1 {{ margin: 0; font-size: 24px; color: #fff; display: flex; align-items: center; gap: 10px; }}
        .nasa-logo {{ background: #0b3d91; color: white; padding: 4px 8px; border-radius: 50%; font-weight: bold; font-family: Arial; font-size: 16px; }}
       
        .panel {{ position: absolute; background: rgba(10, 15, 25, 0.85); border: 1px solid #334; border-radius: 12px; padding: 20px; backdrop-filter: blur(8px); z-index: 10; display: block; }}
        #live-math-panel {{ top: 20px; right: 20px; width: 340px; border-top: 4px solid #00e5ff; box-shadow: 0 4px 20px rgba(0,229,255,0.15); }}
       
        .math-section {{ margin-bottom: 14px; }}
        .math-title {{ font-size: 13px; color: #bbb; margin-bottom: 2px; }}
        .math-live {{ font-size: 19px; color: #fff; font-weight: bold; }}
        .math-eq {{ font-size: 12px; color: #8ab4f8; display: block; margin-top: 4px; background: rgba(0,0,0,0.4); padding: 5px; border-radius: 5px; }}
       
        #lbl-stage {{ color: #00ff00; font-weight: bold; font-size: 15px; background: rgba(0,255,0,0.1); padding: 6px 12px; border-radius: 6px; display: inline-block; margin-top: 12px; border: 1px solid #00ff00; letter-spacing: 1px; text-transform: uppercase; }}
        .guide {{ position: absolute; bottom: 20px; width: 100%; text-align: center; color: #888; font-size: 14px; pointer-events: none; }}
    </style>
</head>
<body>
    <div id="hud">
        <h1><span class="nasa-logo">NASA</span> ARTEMIS II MISSION</h1>
        <div id="lbl-stage">SYSTEM CHECKOUT / 系統檢查</div>
    </div>

    <div id="live-math-panel" class="panel">
        <div class="math-section">
            <div class="math-title">1. 距離向量 (Distance Vector)</div>
            <div class="math-live" style="color:#00e5ff;">Earth: <span id="val-distE">0</span> km</div>
            <div class="math-live" style="color:#ddd;">Moon: <span id="val-distM">0</span> km</div>
            <div class="math-eq">$\\small |\\vec{{r}}| = \\sqrt{{x^2 + y^2}}$</div>
        </div>

        <div class="math-section">
            <div class="math-title">2. 加速度 (Acceleration)</div>
            <div class="math-live" style="color:#ff5555;"><span id="val-acc">0</span> m/s²</div>
            <div class="math-eq">$\\small a = \\frac{{dv}}{{dt}} = \\frac{{d^2r}}{{dt^2}}$</div>
        </div>

        <div class="math-section">
            <div class="math-title">3. 累積弧長 (Arc Length)</div>
            <div class="math-live" style="color:#ffff00;"><span id="val-arc">0</span> km</div>
            <div class="math-eq">$\\small L = \\int \\sqrt{{(dx/dt)^2 + (dy/dt)^2}} dt$</div>
        </div>
    </div>
   
    <div class="guide">滾輪縮放 (Scroll to Zoom) | 左鍵旋轉 (Left Click to Rotate) | 完美八字軌道鎖定 (Perfect Figure-8 Route Locked)</div>

    <script>
        const shipData = {json.dumps(ship_data)};
        const moonData = {json.dumps(moon_data)};
        const liveMath = {json.dumps(live_math)};
        const stagesData = {json.dumps(stagesData)};
        const pathColors = {json.dumps(path_colors)};

        const scene = new THREE.Scene();
        const camera = new THREE.PerspectiveCamera(45, window.innerWidth / window.innerHeight, 0.1, 5000);
        camera.position.set(200, -200, 500);
       
        const renderer = new THREE.WebGLRenderer({{ antialias: true, logarithmicDepthBuffer: true }});
        renderer.setSize(window.innerWidth, window.innerHeight);
        document.body.appendChild(renderer.domElement);
        const controls = new THREE.OrbitControls(camera, renderer.domElement);
        controls.target.set(150, 0, 0);

        scene.add(new THREE.AmbientLight(0x333333));
        const sunLight = new THREE.PointLight(0xffffff, 2.5, 3000);
        sunLight.position.set(500, 300, 150);
        scene.add(sunLight);

        // Earth
        const earth = new THREE.Mesh(new THREE.SphereGeometry(6.371, 64, 64), new THREE.MeshPhongMaterial({{
            map: new THREE.TextureLoader().load('https://raw.githubusercontent.com/mrdoob/three.js/master/examples/textures/planets/earth_atmos_2048.jpg')
        }}));
        scene.add(earth);

        // Moon
        const moonGeo = new THREE.SphereGeometry(6.0, 64, 64);
        const moonMat = new THREE.MeshPhongMaterial({{
            map: new THREE.TextureLoader().load('https://raw.githubusercontent.com/mrdoob/three.js/master/examples/textures/planets/moon_1024.jpg'),
            emissive: 0x111111
        }});
        const moon = new THREE.Mesh(moonGeo, moonMat);
        scene.add(moon);

        // Ship
        const shipGroup = new THREE.Group();
        const esm = new THREE.Mesh(new THREE.CylinderGeometry(1.2, 1.2, 4, 16), new THREE.MeshPhongMaterial({{color: 0xcccccc}}));
        esm.rotation.z = Math.PI/2; shipGroup.add(esm);
       
        const cm = new THREE.Mesh(new THREE.ConeGeometry(1.4, 2.4, 16), new THREE.MeshPhongMaterial({{color: 0xffffff}}));
        cm.position.x = 3.2; cm.rotation.z = -Math.PI/2; shipGroup.add(cm);
        scene.add(shipGroup);

        const MAX_POINTS = shipData.length;
        const lineGeoOutbound = new THREE.BufferGeometry();
        const lineGeoInbound = new THREE.BufferGeometry();
        const posOutbound = new Float32Array(MAX_POINTS * 3);
        const posInbound = new Float32Array(MAX_POINTS * 3);
       
        lineGeoOutbound.setAttribute('position', new THREE.BufferAttribute(posOutbound, 3));
        lineGeoInbound.setAttribute('position', new THREE.BufferAttribute(posInbound, 3));
       
        const lineOutbound = new THREE.Line(lineGeoOutbound, new THREE.LineBasicMaterial({{ color: 0x00ff00, linewidth: 2.5 }}));
        const lineInbound = new THREE.Line(lineGeoInbound, new THREE.LineBasicMaterial({{ color: 0x00aaff, linewidth: 2.5 }}));  
        scene.add(lineOutbound);
        scene.add(lineInbound);

        let frame = 0;
        let outCount = 0;
        let inCount = 0;
        let currentStage = "";

        const elDistE = document.getElementById('val-distE');
        const elDistM = document.getElementById('val-distM');
        const elAcc = document.getElementById('val-acc');
        const elArc = document.getElementById('val-arc');
        const elStage = document.getElementById('lbl-stage');

        function animate() {{
            requestAnimationFrame(animate);
            controls.update();

            if (frame < MAX_POINTS) {{
                earth.rotation.y += 0.005;
                moon.position.set(moonData[frame].x, moonData[frame].y, 0);
                moon.rotation.y += 0.002;

                const sx = shipData[frame].x;
                const sy = shipData[frame].y;
                shipGroup.position.set(sx, sy, 0);

                if (frame < MAX_POINTS - 1) {{
                    const nx = shipData[frame+1].x;
                    const ny = shipData[frame+1].y;
                    shipGroup.rotation.z = Math.atan2(ny - sy, nx - sx);
                }}

                if (pathColors[frame] === "green") {{
                    posOutbound[outCount*3] = sx; posOutbound[outCount*3+1] = sy; posOutbound[outCount*3+2] = 0;
                    lineGeoOutbound.attributes.position.needsUpdate = true;
                    lineGeoOutbound.setDrawRange(0, outCount + 1);
                    outCount++;
                }} else {{
                    if(inCount === 0 && frame > 0) {{
                        posInbound[0] = shipData[frame-1].x; posInbound[1] = shipData[frame-1].y; posInbound[2] = 0;
                        inCount++;
                    }}
                    posInbound[inCount*3] = sx; posInbound[inCount*3+1] = sy; posInbound[inCount*3+2] = 0;
                    lineGeoInbound.attributes.position.needsUpdate = true;
                    lineGeoInbound.setDrawRange(0, inCount + 1);
                    inCount++;
                }}

                const newStage = stagesData[frame];
                if (newStage !== currentStage) {{
                    elStage.innerText = newStage;
                    if (newStage.includes("Trans-Earth")) {{
                        elStage.style.color = "#00aaff"; elStage.style.borderColor = "#00aaff"; elStage.style.backgroundColor = "rgba(0,170,255,0.1)";
                    }} else if (newStage.includes("Splashdown")) {{
                        shipGroup.remove(esm);
                        elStage.style.color = "#ff5555"; elStage.style.borderColor = "#ff5555"; elStage.style.backgroundColor = "rgba(255,85,85,0.1)";
                    }}
                    currentStage = newStage;
                }}

                if (frame % 3 === 0) {{
                    const math = liveMath[frame];
                    elDistE.innerText = math.dist_E.toLocaleString();
                    elDistM.innerText = math.dist_M.toLocaleString();
                    elAcc.innerText = math.acc;
                    elArc.innerText = math.arc.toLocaleString();
                }}

                frame += 1;
            }}
            renderer.render(scene, camera);
        }}

        window.addEventListener('resize', () => {{
            camera.aspect = window.innerWidth / window.innerHeight;
            camera.updateProjectionMatrix();
            renderer.setSize(window.innerWidth, window.innerHeight);
        }});

        setTimeout(animate, 500);
    </script>
</body>
</html>"""

filename = "artemis2_nasa_zh_en.html"
with open(filename, "w", encoding="utf-8") as f:
    f.write(html_content)

webbrowser.open('file://' + os.path.realpath(filename))
print("🚀 軌道座標已修正，成功建立並開啟網頁！")