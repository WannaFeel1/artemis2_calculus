import math
import json
import webbrowser
import os

# ==========================================
# 1. 3D Kinematic & Parametric Engine (Artemis II NASA Data)
# ==========================================
D_moon = 384.4       
omega_moon = 0.00266
tilt = 0.087 # ความเอียงวงโคจร ~5 องศา

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
            raw_ax = (vx - prev["vx"]) / 0.1
            raw_ay = (vy - prev["vy"]) / 0.1
            raw_az = (vz - prev["vz"]) / 0.1
            ax = prev["ax"] * 0.5 + raw_ax * 0.5
            ay = prev["ay"] * 0.5 + raw_ay * 0.5
            az = prev["az"] * 0.5 + raw_az * 0.5

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

# --- Orbit Calculations ---
for i in range(100):
    th = math.pi + (i/100) * (2*math.pi)
    record_frame(6.8 * math.cos(th), 6.8 * math.sin(th) * math.cos(tilt), 6.8 * math.sin(th) * math.sin(tilt), "1. 發射與近地軌道 / LEO Checkout", "green")

for i in range(150):
    th = math.pi + (i/150) * (2*math.pi)
    r = (20 * (1 - 0.65**2)) / (1 - 0.65 * math.cos(th))
    record_frame(r * math.cos(th), r * math.sin(th) * math.cos(tilt), r * math.sin(th) * math.sin(tilt), "2. 遠地點提升 / Apogee Raise (HEO)", "green")

tli_steps = 800
last = ship_data[-1]
for i in range(tli_steps):
    t = i / tli_steps
    ft = time + (tli_steps - i)*0.1
    tmx = D_moon * math.cos(omega_moon * ft)
    tmy = D_moon * math.sin(omega_moon * ft) * math.cos(tilt)
    tmz = D_moon * math.sin(omega_moon * ft) * math.sin(tilt)
    p0 = (last["x"], last["y"], last["z"])
    p1 = (100, -150, 10); p2 = (300, -50, -10); p3 = (tmx + 10.4, tmy - 10.4, tmz + 5) 
    x, y, z = get_bezier_point_3d(t, p0, p1, p2, p3)
    record_frame(x, y, z, "3. 地月轉移 / TLI & Outbound Transit", "green")

flyby_steps = 150
for i in range(flyby_steps):
    t = i / flyby_steps
    mx = D_moon * math.cos(omega_moon * time)
    my = D_moon * math.sin(omega_moon * time) * math.cos(tilt)
    mz = D_moon * math.sin(omega_moon * time) * math.sin(tilt)
    a = -math.pi/4 + (t * math.pi)
    r = 10.4 - (math.sin(t * math.pi) * 3) 
    record_frame(mx + r*math.cos(a), my + r*math.sin(a)*math.cos(tilt), mz + r*math.sin(a)*math.sin(tilt), "4. 繞月飛行 (月球背面) / Lunar Flyby", "blue")

return_steps = 800
last = ship_data[-1]
for i in range(return_steps):
    t = i / return_steps
    p0 = (last["x"], last["y"], last["z"])
    p1 = (250, 180, -15); p2 = (50, 80, 5); p3 = (-6.8, 0, 0)
    x, y, z = get_bezier_point_3d(t, p0, p1, p2, p3)
    record_frame(x, y, z, "5. 返回地球 / Trans-Earth Return", "blue")

for i in range(15): record_frame(-6.8, 0, 0, "6. 濺落與回收 / Splashdown", "blue")

# ==========================================
# 2. Web Engine & HTML (Ultimate Educational Version)
# ==========================================
html_content = f"""<!DOCTYPE html>
<html lang="zh-TW">
<head>
    <meta charset="UTF-8">
    <title>NASA Artemis II - Calculus & Physics Simulator</title>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/three@0.128.0/examples/js/controls/OrbitControls.js"></script>
    <style>
        body {{ margin: 0; overflow: hidden; background: #000; font-family: 'Consolas', monospace; color: #fff; }}
        
        .ui-element {{ transition: opacity 0.4s ease; }}
        #hud {{ position: absolute; top: 20px; left: 20px; z-index: 10; pointer-events: none; }}
        #hud h1 {{ margin: 0; display: flex; align-items: center; gap: 12px; }}
        .header-logo {{ height: 45px; object-fit: contain; filter: drop-shadow(0 2px 4px rgba(0,0,0,0.8)); }}
        #mission-time {{ font-size: 20px; color: #ff9900; font-weight: bold; margin-top: 10px; letter-spacing: 2px; text-shadow: 0 0 10px rgba(255,153,0,0.5); }}
        #lbl-stage {{ color: #00ff00; font-size: 14px; background: rgba(0,255,0,0.1); padding: 6px 12px; border-radius: 6px; display: inline-block; margin-top: 8px; border: 1px solid #00ff00; backdrop-filter: blur(5px); }}
        
        #ntut-logo-btn {{ position: absolute; bottom: 20px; left: 20px; height: 50px; z-index: 50; cursor: pointer; background: rgba(255, 255, 255, 0.9); padding: 8px 15px; border-radius: 8px; box-shadow: 0 0 15px rgba(0, 229, 255, 0.3); transition: all 0.3s ease; pointer-events: auto; }}
        #ntut-logo-btn:hover {{ transform: scale(1.05) translateY(-5px); box-shadow: 0 5px 25px rgba(0, 229, 255, 0.8); }}
        
        #ntut-overlay {{ display: none; position: absolute; top: 50%; left: 50%; transform: translate(-50%, -50%); z-index: 200; text-align: center; pointer-events: none; }}
        .ntut-title {{ font-size: 40px; font-weight: bold; color: #00e5ff; text-shadow: 0 0 20px #00e5ff, 0 0 40px #1a73e8, 0 5px 5px rgba(0,0,0,0.8); letter-spacing: 2px; }}
        .ntut-subtitle {{ font-size: 24px; color: #fff; margin-top: 10px; font-style: italic; text-shadow: 0 0 10px rgba(255,255,255,0.8); }}
        
        @keyframes fadeInOut {{
            0% {{ opacity: 0; transform: translate(-50%, -40%) scale(0.9); }}
            15% {{ opacity: 1; transform: translate(-50%, -50%) scale(1); }}
            85% {{ opacity: 1; transform: translate(-50%, -50%) scale(1); }}
            100% {{ opacity: 0; transform: translate(-50%, -60%) scale(1.1); }}
        }}

        #cam-controls {{ position: absolute; bottom: 20px; left: 50%; transform: translateX(-50%); z-index: 20; display: flex; gap: 8px; background: rgba(10,15,25,0.8); padding: 8px; border-radius: 8px; border: 1px solid #334; backdrop-filter: blur(5px); }}
        .cam-btn {{ background: rgba(26, 115, 232, 0.2); color: #8ab4f8; border: 1px solid transparent; padding: 10px 15px; cursor: pointer; border-radius: 6px; font-weight: bold; transition: 0.3s; font-family: 'Consolas'; }}
        .cam-btn:hover {{ background: rgba(26, 115, 232, 0.4); }}
        .cam-btn.active {{ background: #1a73e8; color: #fff; border-color: #4285f4; box-shadow: 0 0 10px rgba(26,115,232,0.5); }}
        
        #panel-toggle {{ position: absolute; top: 20px; right: 20px; z-index: 30; background: #1a73e8; color: white; border: none; padding: 8px 12px; border-radius: 6px; font-weight: bold; cursor: pointer; font-family: Consolas; transition: 0.3s; }}
        #panel-toggle:hover {{ background: #1557b0; }}
        
        /* Clean HUD Panel */
        .panel {{ position: absolute; top: 60px; right: 20px; width: 300px; background: rgba(10, 15, 25, 0.85); border: 1px solid #334; border-radius: 12px; padding: 20px; backdrop-filter: blur(8px); border-top: 4px solid #00e5ff; z-index: 10; box-shadow: 0 5px 20px rgba(0,0,0,0.5); display: block; }}
        .math-section {{ margin-bottom: 12px; border-bottom: 1px solid #223; padding-bottom: 8px; }}
        .math-title {{ font-size: 13px; color: #bbb; margin-bottom: 4px; font-weight: bold; }}
        .math-result {{ font-size: 22px; color: #00e5ff; font-weight: bold; }}
        
        /* Fixed Buttons */
        .btn-container {{ position: absolute; bottom: 100px; left: 20px; z-index: 20; display: flex; gap: 10px; flex-direction: column; }}
        .btn {{ background: rgba(26, 115, 232, 0.2); color: #8ab4f8; border: 1px solid #1a73e8; padding: 12px 20px; border-radius: 8px; cursor: pointer; font-weight: bold; transition: 0.3s; backdrop-filter: blur(5px); text-align: left; font-family: 'Consolas'; display: flex; align-items: center; gap: 10px; }}
        .btn:hover {{ background: rgba(26, 115, 232, 0.6); color: white; }}
        .btn-replay {{ border-color: #ff9900; color: #ff9900; background: rgba(255, 153, 0, 0.1); }}
        
        #btn-exit-cinematic {{ display: none; position: absolute; top: 20px; right: 20px; background: rgba(255,0,0,0.6); color: white; border: 1px solid red; padding: 10px 20px; border-radius: 6px; z-index: 100; cursor: pointer; font-family: Consolas; font-weight: bold; }}
        #btn-exit-cinematic:hover {{ background: red; }}

        /* Educational Calculus Modal */
        #desmos-modal {{ display: none; position: absolute; top: 50%; left: 50%; transform: translate(-50%, -50%); width: 95vw; height: 90vh; max-width: 1500px; background: rgba(10, 12, 18, 0.95); border: 1px solid #334; border-radius: 12px; z-index: 100; box-shadow: 0 10px 50px rgba(0,0,0,0.9); flex-direction: row; overflow: hidden; }}
        .desmos-sidebar {{ width: 42%; padding: 20px; border-right: 1px solid #223; background: rgba(0,0,0,0.3); overflow-y: auto; }}
        .desmos-canvas-container {{ width: 58%; position: relative; background: #050505; display: flex; flex-direction: column; overflow: hidden; }}
        
        .modal-toolbar {{ display: flex; align-items: center; background: #111; border-bottom: 1px solid #333; padding-right: 15px; flex-shrink: 0; z-index: 2; height: 50px; }}
        .graph-tabs {{ display: flex; height: 100%; }}
        .g-tab {{ padding: 15px 30px; text-align: center; cursor: pointer; color: #888; background: #0a0a0a; border-right: 1px solid #222; font-weight: bold; transition: 0.2s; user-select: none; display: flex; align-items: center; justify-content: center; }}
        .g-tab:hover {{ background: #151515; }}
        .g-tab.active {{ color: #00e5ff; background: #1a1a1a; box-shadow: inset 0 -3px 0 #00e5ff; }}
        
        .btn-fullscreen {{ background: rgba(255,255,255,0.1); color: #fff; border: 1px solid #555; padding: 6px 12px; border-radius: 4px; cursor: pointer; font-size: 13px; margin-left: auto; transition: 0.3s; font-family: 'Consolas'; }}
        .btn-fullscreen:hover {{ background: #1a73e8; border-color: #1a73e8; }}
        .modal-close {{ background: rgba(255,0,0,0.2); border: 1px solid #ff5555; color: #fff; font-size: 16px; cursor: pointer; width: 30px; height: 30px; border-radius: 50%; display: flex; align-items: center; justify-content: center; margin-left: 15px; transition: 0.2s; }}
        .modal-close:hover {{ background: #ff5555; }}
        
        .graph-content-area {{ flex-grow: 1; position: relative; width: 100%; height: calc(100% - 50px); }}
        #desmos-grid {{ position: absolute; top: 0; left: 0; width: 100%; height: 100%; display: block; }}
        #graph-3d-container {{ position: absolute; top: 0; left: 0; width: 100%; height: 100%; display: none; overflow: hidden; }}
        
        /* 3D Dynamic HUD Elements */
        .hud-3d-label {{ position: absolute; font-family: 'Consolas', monospace; font-weight: bold; font-size: 12px; pointer-events: none; z-index: 10; display: none; text-shadow: 1px 1px 2px #000; }}
        #hud-3d-ship {{ background: rgba(0,0,0,0.7); color: #fff; padding: 6px 10px; border-radius: 4px; border-left: 3px solid #00e5ff; font-size: 13px; }}
        #hud-3d-x {{ color: #ff5555; }}
        #hud-3d-y {{ color: #00ff00; }}
        #hud-3d-z {{ color: #00aaff; }}
        
        .eq-box {{ background: rgba(25,30,40,0.6); border-left: 4px solid #1a73e8; padding: 12px; margin-bottom: 12px; border-radius: 4px; font-size: 13px; color: #ccc; backdrop-filter: blur(5px); }}
        .eq-hl {{ color: #fff; font-family: monospace; background: rgba(0,0,0,0.5); padding: 8px; border-radius: 4px; display: block; margin-top: 6px; font-size: 13px; border: 1px solid #333; }}
        
        .desmos-sidebar::-webkit-scrollbar {{ width: 8px; }}
        .desmos-sidebar::-webkit-scrollbar-track {{ background: rgba(0,0,0,0.1); }}
        .desmos-sidebar::-webkit-scrollbar-thumb {{ background: #334; border-radius: 4px; }}
    </style>
</head>
<body>
    <div id="hud" class="ui-element">
        <h1>
            <img src="image_1.png" alt="NASA" class="header-logo" onerror="this.style.display='none'">
            <img src="image_0.png" alt="Artemis II" class="header-logo" onerror="this.style.display='none'">
            <span style="letter-spacing: 2px;">ARTEMIS II</span>
        </h1>
        <div id="mission-time">MET: T+ 00:00:00:00</div>
        <div id="lbl-stage">SYSTEM CHECKOUT</div>
    </div>

    <!-- NTUT Zoom Interaction Overlay -->
    <div id="ntut-overlay">
        <div class="ntut-title">National Taipei University of Technology</div>
        <div class="ntut-subtitle">is here</div>
    </div>

    <img id="ntut-logo-btn" src="image_2.png" alt="NTUT" onclick="zoomToNTUT()" title="Locate NTUT" onerror="this.style.display='none'">

    <div id="cam-controls" class="ui-element">
        <button class="cam-btn active" id="btn-cam-free" onclick="setCamera('free')">🎥 自由視角 / Free Cam</button>
        <button class="cam-btn" id="btn-cam-ship" onclick="setCamera('ship')">🚀 太空船視角 / Ship POV</button>
        <button class="cam-btn" id="btn-cam-moon" onclick="setCamera('moon')">🌕 月球視角 / Moon POV</button>
        <button class="cam-btn" id="btn-cam-earth" onclick="setCamera('earth')">🌍 Earth POV</button>
    </div>

    <button id="panel-toggle" class="ui-element" onclick="toggleMainPanel()">[ - ] Hide Info</button>
    <button id="btn-exit-cinematic" onclick="toggleCinematic()">✖ 退出沉浸模式 / Exit Cinematic</button>

    <!-- Clean HUD Panel -->
    <div id="live-math-panel" class="panel ui-element">
        <div class="math-section">
            <div class="math-title">與地球距離 / Distance to Earth</div>
            <div class="math-result" id="hud-dist-earth">0 km</div>
        </div>
        <div class="math-section">
            <div class="math-title">與月球距離 / Distance to Moon</div>
            <div class="math-result" id="hud-dist-moon" style="color:#ff9900;">0 km</div>
        </div>
        <div class="math-section" style="border-bottom:none;">
            <div class="math-title">即時速度 / Velocity</div>
            <div class="math-result" id="hud-vel" style="color:#00ff00;">0.00 km/s</div>
        </div>
    </div>
    
    <div class="btn-container ui-element">
        <button class="btn" onclick="toggleTrajectory()">👁️ 隱藏/顯示軌跡 / Toggle Orbit</button>
        <button class="btn" onclick="toggleCinematic()">🎬 沉浸模式 / Cinematic Mode</button>
        <button class="btn" onclick="toggleDesmos()" style="border-color: #00e5ff; color: #00e5ff;">📈 大學微積分圖表 / Vector Calculus Modal</button>
        <button class="btn btn-replay" onclick="replayMission()">↺ 重新播放 / Replay Mission</button>
    </div>

    <!-- Advanced Educational Calculus Modal -->
    <div id="desmos-modal">
        <div class="desmos-sidebar">
            <h3 style="color:#00e5ff; margin-top:0; border-bottom: 1px solid #334; padding-bottom: 8px;">即時向量計算 (Live Vector Calculations)</h3>
            <div class="eq-box" style="border-color:#1a73e8;">
                <b>1. 3D 距離向量 / 3D Distance Vector</b><br>
                |r| = &radic;(x&sup2; + y&sup2; + z&sup2;)<br>
                <span class="eq-hl" id="calc-sub-pos">Calculating...</span>
            </div>
            <div class="eq-box" style="border-color:#00ff00;">
                <b>2. 3D 速度向量 / 3D Velocity Mag.</b><br>
                |v| = &radic;(vx&sup2; + vy&sup2; + vz&sup2;)<br>
                <span class="eq-hl" id="calc-sub-vel">Calculating...</span>
            </div>
            <div class="eq-box" style="border-color:#ffff00;">
                <b>3. 動力學狀態 / Dynamic State</b><br>
                a = v'(t) (加速度) | L = &int; |v| dt (弧長)<br>
                <span class="eq-hl" id="calc-sub-acc">Calculating...</span>
            </div>
            
            <h3 style="color:#ff5555; margin-top:20px; border-bottom: 1px solid #334; padding-bottom: 8px;">大學微積分 (Undergraduate Vector Calculus)</h3>
            <div class="eq-box" style="border-color:#ff5555;">
                <b>弗萊納-塞雷公式 (Frenet-Serret Frame)</b><br>
                T(t) = v / |v| (單位切向量)<br>
                N(t) = T' / |T'| (單位法向量)<br>
                B(t) = T &times; N (副法向量)<br>
                <span class="eq-hl" id="calc-frenet">Calculating...</span>
            </div>
            <div class="eq-box" style="border-color:#ff00ff;">
                <b>高階導數與扭率 (Jerk & Torsion)</b><br>
                j(t) = a'(t) (急動度 / Jerk)<br>
                &tau; = (v &times; a) &middot; j / |v &times; a|&sup2; (扭率)<br>
                <span class="eq-hl" id="calc-torsion">Calculating...</span>
            </div>
            <div class="eq-box" style="border-color:#ff9900;">
                <b>作功線積分 (Line Integral of Work)</b><br>
                W = &int; F &middot; dr (重力對太空船作功)<br>
                (Energy transfers between Kinetic and Potential)<br>
                <span class="eq-hl" id="calc-work">Calculating...</span>
            </div>
            <div class="eq-box" style="border-color:#ff0000;">
                <b>特定軌道能 (Vis-viva Integral)</b><br>
                &epsilon; = v&sup2;/2 - &mu;/r<br>
                <span class="eq-hl" id="calc-eng">Calculating...</span>
            </div>

            <h3 style="color:#00ffcc; margin-top:20px; border-bottom: 1px solid #334; padding-bottom: 8px;">本機模擬核心數學 (Simulation Core Mathematics)</h3>
            <div class="eq-box" style="border-color:#00ffcc;">
                <b>1. 月球參數方程式 (Moon Parametric Eq)</b><br>
                D = 384.4, &omega; = 0.00266, Tilt = 5&deg; (0.087 rad)<br>
                <span class="eq-hl">
                    x_m(t) = 384.4 &times; cos(0.00266t)<br>
                    y_m(t) = 384.4 &times; sin(0.00266t) &times; cos(0.087)<br>
                    z_m(t) = 384.4 &times; sin(0.00266t) &times; sin(0.087)
                </span>
            </div>
            <div class="eq-box" style="border-color:#00ffcc;">
                <b>2. 三次方貝茲曲線 (Cubic Bézier Curve - TLI)</b><br>
                B(t) = (1-t)&sup3;P₀ + 3(1-t)&sup2;tP₁ + 3(1-t)t&sup2;P₂ + t&sup3;P₃<br>
                <span class="eq-hl" style="color:#aaa;">
                    P₀ = (x₀, y₀, z₀) [LEO Exit]<br>
                    P₁ = (100, -150, 10)<br>
                    P₂ = (300, -50, -10)<br>
                    P₃ = (x_m + 10.4, y_m - 10.4, z_m + 5)
                </span>
            </div>
            <div class="eq-box" style="border-color:#00ffcc;">
                <b>3. 高橢圓軌道 (HEO Elliptical Orbit)</b><br>
                r(&theta;) = a(1 - e&sup2;) / (1 - e &times; cos&theta;)<br>
                a = 20, e = 0.65<br>
                <span class="eq-hl">
                    r(&theta;) = 20(1 - 0.4225) / (1 - 0.65cos&theta;)<br>
                    r(&theta;) = 11.55 / (1 - 0.65cos&theta;)
                </span>
            </div>
        </div>
        
        <div class="desmos-canvas-container">
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
                    <!-- 3D HUD Tracking Elements -->
                    <div id="hud-3d-ship" class="hud-3d-label">Ship(0,0,0)</div>
                    <div id="hud-3d-x" class="hud-3d-label">X 軸 (Axis)</div>
                    <div id="hud-3d-y" class="hud-3d-label">Y 軸 (Axis)</div>
                    <div id="hud-3d-z" class="hud-3d-label">Z 軸 (Axis)</div>
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

        const ORION_MASS = 26500; 

        // --- MAIN 3D Scene ---
        const scene = new THREE.Scene();
        const camera = new THREE.PerspectiveCamera(45, window.innerWidth/window.innerHeight, 0.1, 5000);
        camera.position.set(200, -200, 500);
        const renderer = new THREE.WebGLRenderer({{ antialias: true, logarithmicDepthBuffer: true }});
        renderer.setSize(window.innerWidth, window.innerHeight);
        
        renderer.shadowMap.enabled = true;
        renderer.shadowMap.type = THREE.PCFSoftShadowMap;
        document.body.appendChild(renderer.domElement);
        
        const controls = new THREE.OrbitControls(camera, renderer.domElement);
        controls.enableDamping = true;

        scene.add(new THREE.AmbientLight(0x222222)); 
        const sunLight = new THREE.DirectionalLight(0xffffff, 2.0);
        sunLight.position.set(500, 300, 150); 
        sunLight.castShadow = true;
        sunLight.shadow.mapSize.width = 2048;
        sunLight.shadow.mapSize.height = 2048;
        sunLight.shadow.camera.near = 100;
        sunLight.shadow.camera.far = 1000;
        sunLight.shadow.camera.left = -200;
        sunLight.shadow.camera.right = 200;
        sunLight.shadow.camera.top = 200;
        sunLight.shadow.camera.bottom = -200;
        scene.add(sunLight);

        const starGeo = new THREE.BufferGeometry();
        const starPts = new Float32Array(3000);
        for(let i=0; i<3000; i++) starPts[i] = (Math.random()-0.5)*2000;
        starGeo.setAttribute('position', new THREE.BufferAttribute(starPts, 3));
        scene.add(new THREE.Points(starGeo, new THREE.PointsMaterial({{color: 0xffffff, size: 1.2}})));

        const earthMat = new THREE.MeshStandardMaterial({{map: new THREE.TextureLoader().load('https://raw.githubusercontent.com/mrdoob/three.js/master/examples/textures/planets/earth_atmos_2048.jpg'), roughness: 0.8}});
        const earth = new THREE.Mesh(new THREE.SphereGeometry(6.371, 64, 64), earthMat);
        earth.castShadow = true; earth.receiveShadow = true;
        scene.add(earth);

        const taipeiPhi = (90 - 25.04) * Math.PI / 180;
        const taipeiTheta = (121.53 + 90) * Math.PI / 180; 
        
        const ntutMarker = new THREE.Mesh(new THREE.SphereGeometry(0.04, 16, 16), new THREE.MeshBasicMaterial({{color: 0x00e5ff}}));
        ntutMarker.position.setFromSphericalCoords(6.371, taipeiPhi, taipeiTheta);
        const ntutRing = new THREE.Mesh(new THREE.RingGeometry(0.06, 0.1, 32), new THREE.MeshBasicMaterial({{color: 0x00e5ff, transparent: true, opacity: 0.8, side: THREE.DoubleSide}}));
        ntutRing.position.setFromSphericalCoords(6.38, taipeiPhi, taipeiTheta);
        ntutRing.lookAt(new THREE.Vector3(0,0,0));
        earth.add(ntutMarker); earth.add(ntutRing);

        const moonMat = new THREE.MeshStandardMaterial({{map: new THREE.TextureLoader().load('https://raw.githubusercontent.com/mrdoob/three.js/master/examples/textures/planets/moon_1024.jpg'), roughness: 1.0}});
        const moon = new THREE.Mesh(new THREE.SphereGeometry(6.0, 64, 64), moonMat);
        moon.castShadow = true; moon.receiveShadow = true;
        scene.add(moon);
        
        const orbitGeo = new THREE.BufferGeometry();
        const oPts = [];
        for(let i=0; i<=100; i++) {{
            let a = (i/100) * Math.PI * 2;
            oPts.push(new THREE.Vector3(384.4 * Math.cos(a), 384.4 * Math.sin(a) * Math.cos(0.087), 384.4 * Math.sin(a) * Math.sin(0.087)));
        }}
        orbitGeo.setFromPoints(oPts);
        const orbitLine = new THREE.Line(orbitGeo, new THREE.LineBasicMaterial({{color: 0x444444, transparent: true, opacity: 0.6}}));
        scene.add(orbitLine);

        // 🚀 HIGH-DETAIL PROCEDURAL ORION SPACECRAFT MODEL WITH SHADOWS
        const shipGroup = new THREE.Group();
        
        const matSilver = new THREE.MeshStandardMaterial({{color: 0xcccccc, metalness: 0.8, roughness: 0.3}});
        const matWhite = new THREE.MeshStandardMaterial({{color: 0xeeeeee, metalness: 0.1, roughness: 0.8}});
        const matBlack = new THREE.MeshStandardMaterial({{color: 0x111111, metalness: 0.2, roughness: 0.5}});
        const matGold = new THREE.MeshStandardMaterial({{color: 0xd4af37, metalness: 0.9, roughness: 0.4}});
        
        const cmGroup = new THREE.Group();
        const cm = new THREE.Mesh(new THREE.ConeGeometry(0.8, 1.0, 32), matSilver);
        cm.rotation.x = -Math.PI/2; 
        cm.castShadow = true; cm.receiveShadow = true;
        const dock = new THREE.Mesh(new THREE.CylinderGeometry(0.25, 0.25, 0.2, 16), matSilver);
        dock.position.z = 0.6; dock.rotation.x = Math.PI/2;
        cmGroup.add(cm); cmGroup.add(dock);
        cmGroup.position.x = 1.0; cmGroup.rotation.y = Math.PI/2;
        shipGroup.add(cmGroup);

        const skirt = new THREE.Mesh(new THREE.CylinderGeometry(0.8, 0.8, 0.4, 32), matBlack);
        skirt.position.x = 0.3; skirt.rotation.z = Math.PI/2;
        skirt.castShadow = true; skirt.receiveShadow = true;
        shipGroup.add(skirt);

        const esm = new THREE.Mesh(new THREE.CylinderGeometry(0.8, 0.8, 1.4, 32), matWhite);
        esm.position.x = -0.6; esm.rotation.z = Math.PI/2; 
        esm.castShadow = true; esm.receiveShadow = true;
        for(let i=0; i<8; i++) {{
            const greeble = new THREE.Mesh(new THREE.BoxGeometry(0.2, 0.4, 0.2), matSilver);
            const angle = (i/8) * Math.PI * 2;
            greeble.position.set(Math.cos(angle)*0.75, 0, Math.sin(angle)*0.75);
            esm.add(greeble);
        }}
        shipGroup.add(esm);
        
        const engine = new THREE.Mesh(new THREE.CylinderGeometry(0.1, 0.4, 0.6, 16, 1, true), matGold);
        engine.position.x = -1.6; engine.rotation.z = -Math.PI/2; 
        engine.castShadow = true;
        shipGroup.add(engine);

        const canvas = document.createElement('canvas');
        canvas.width = 64; canvas.height = 64;
        const context = canvas.getContext('2d');
        context.fillStyle = '#0a3b70'; context.fillRect(0,0,64,64);
        context.strokeStyle = '#225599'; context.lineWidth = 2;
        context.strokeRect(0,0,64,64); context.beginPath(); context.moveTo(32,0); context.lineTo(32,64); context.moveTo(0,32); context.lineTo(64,32); context.stroke();
        const panelTexture = new THREE.CanvasTexture(canvas);
        panelTexture.wrapS = THREE.RepeatWrapping; panelTexture.wrapT = THREE.RepeatWrapping;
        panelTexture.repeat.set(1, 4);
        
        const solarMat = new THREE.MeshStandardMaterial({{map: panelTexture, metalness: 0.5, roughness: 0.2}});
        for(let i=0; i<4; i++) {{
            const panelGroup = new THREE.Group();
            const truss = new THREE.Mesh(new THREE.CylinderGeometry(0.05, 0.05, 1.5, 8), matBlack);
            truss.position.z = 0.75; truss.rotation.x = Math.PI/2;
            const panel = new THREE.Mesh(new THREE.BoxGeometry(1.2, 0.05, 4.0), solarMat);
            panel.position.z = 3.0; 
            panel.castShadow = true;
            panelGroup.add(truss); panelGroup.add(panel);
            panelGroup.position.x = -0.6;
            panelGroup.rotation.x = (i * Math.PI) / 2 + Math.PI/4; 
            panelGroup.rotation.y = -Math.PI/12; 
            shipGroup.add(panelGroup);
        }}
        scene.add(shipGroup);

        const lineGeoOut = new THREE.BufferGeometry();
        const lineGeoIn = new THREE.BufferGeometry();
        const posOut = new Float32Array(MAX * 3);
        const posIn = new Float32Array(MAX * 3);
        lineGeoOut.setAttribute('position', new THREE.BufferAttribute(posOut, 3));
        lineGeoIn.setAttribute('position', new THREE.BufferAttribute(posIn, 3));
        const mainLineOut = new THREE.Line(lineGeoOut, new THREE.LineBasicMaterial({{color: 0x00ff00}}));
        const mainLineIn = new THREE.Line(lineGeoIn, new THREE.LineBasicMaterial({{color: 0x00aaff}}));
        scene.add(mainLineOut); scene.add(mainLineIn);

        // --- SUB 3D Scene (Modal Graph) ---
        const subContainer = document.getElementById('graph-3d-container');
        const subScene = new THREE.Scene();
        const subCamera = new THREE.PerspectiveCamera(50, 1, 0.1, 2000);
        subCamera.position.set(200, 200, 300); 
        const subRenderer = new THREE.WebGLRenderer({{ alpha: true, antialias: true }});
        subContainer.appendChild(subRenderer.domElement);
        const subControls = new THREE.OrbitControls(subCamera, subRenderer.domElement);
        subControls.enableDamping = true;
        
        const axesH = new THREE.AxesHelper(150); subScene.add(axesH); 
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
        let globalFrame = 0, shipFrame = 0, outC = 0, inC = 0;
        let isDesmos = false, gMode = '2D', camMode = 'free';
        const ctx2d = document.getElementById('desmos-grid').getContext('2d');

        function toggleMainPanel() {{
            const p = document.getElementById('live-math-panel');
            const btn = document.getElementById('panel-toggle');
            if (p.style.display === 'none') {{
                p.style.display = 'block';
                btn.innerText = '[ - ] Hide Math Panel';
            }} else {{
                p.style.display = 'none';
                btn.innerText = '[ + ] Show Math Panel';
            }}
        }}

        function toggleTrajectory() {{
            mainLineOut.visible = !mainLineOut.visible;
            mainLineIn.visible = mainLineOut.visible;
            orbitLine.visible = mainLineOut.visible;
        }}

        function toggleCinematic() {{
            const uis = document.querySelectorAll('.ui-element');
            const isHidden = uis[0].style.opacity === '0';
            uis.forEach(el => {{
                el.style.opacity = isHidden ? '1' : '0';
                el.style.pointerEvents = isHidden ? 'auto' : 'none';
            }});
            document.getElementById('btn-exit-cinematic').style.display = isHidden ? 'none' : 'block';
        }}

        function toggleFullscreenGraph() {{
            const container = document.getElementById('graph-content-area');
            if (!document.fullscreenElement) container.requestFullscreen().catch(e => console.log(e));
            else document.exitFullscreen();
        }}

        document.addEventListener('fullscreenchange', () => {{
            if(isDesmos) setTimeout(() => {{
                const area = document.getElementById('graph-content-area');
                if(gMode === '2D') {{
                    document.getElementById('desmos-grid').width = area.clientWidth; 
                    document.getElementById('desmos-grid').height = area.clientHeight;
                }} else {{
                    subRenderer.setSize(area.clientWidth, area.clientHeight);
                    subCamera.aspect = area.clientWidth / area.clientHeight;
                    subCamera.updateProjectionMatrix();
                }}
            }}, 150); 
        }});

        function toggleDesmos() {{ 
            isDesmos = !isDesmos; 
            document.getElementById('desmos-modal').style.display = isDesmos ? 'flex' : 'none'; 
            if(isDesmos) {{
                const area = document.getElementById('graph-content-area');
                document.getElementById('desmos-grid').width = area.clientWidth; 
                document.getElementById('desmos-grid').height = area.clientHeight;
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
            if(m === '3D') {{
                const area = document.getElementById('graph-content-area');
                subRenderer.setSize(area.clientWidth, area.clientHeight);
                subCamera.aspect = area.clientWidth / area.clientHeight;
                subCamera.updateProjectionMatrix();
            }}
        }}
        
        function setCamera(m) {{ 
            camMode = m; 
            document.querySelectorAll('.cam-btn').forEach(b => b.classList.remove('active'));
            if(document.getElementById('btn-cam-'+m)) document.getElementById('btn-cam-'+m).classList.add('active');
        }}

        window.zoomToNTUT = function() {{
            setCamera('ntut');
            const overlay = document.getElementById('ntut-overlay');
            overlay.style.display = 'block';
            overlay.style.animation = 'none';
            overlay.offsetHeight; 
            overlay.style.animation = 'fadeInOut 5s ease-in-out forwards';
            setTimeout(() => {{ overlay.style.display = 'none'; }}, 5000);
        }}
        
        window.replayMission = function() {{ shipFrame = outC = inC = globalFrame = 0; lineGeoOut.setDrawRange(0,0); lineGeoIn.setDrawRange(0,0); shipGroup.visible = true; setCamera('free'); }};

        function getMET(f) {{
            let ts = Math.floor(f * (864000 / MAX));
            let d = Math.floor(ts/86400); ts %= 86400;
            let h = Math.floor(ts/3600); ts %= 3600;
            let m = Math.floor(ts/60); let s = ts%60;
            return 'MET: T+ ' + String(d).padStart(2,'0') + ':' + String(h).padStart(2,'0') + ':' + String(m).padStart(2,'0') + ':' + String(s).padStart(2,'0');
        }}

        const camTargetPos = new THREE.Vector3();
        const camLookTarget = new THREE.Vector3();

        // Helper to update 3D HTML Labels
        function update3DLabel(id, pos3D, isVisible) {{
            const el = document.getElementById(id);
            if(!isVisible) {{ el.style.display = 'none'; return; }}
            const v = pos3D.clone().project(subCamera);
            if(v.z > 1) {{ el.style.display = 'none'; return; }} // Behind camera
            
            const area = document.getElementById('graph-content-area');
            const x = (v.x * 0.5 + 0.5) * area.clientWidth;
            const y = (-(v.y * 0.5) + 0.5) * area.clientHeight;
            
            el.style.display = 'block';
            el.style.left = (x + 10) + 'px';
            el.style.top = (y - 15) + 'px';
        }}

        function updateCalculusHTML(activeS, prevS, mx, my, mz) {{
            const v2 = activeS.vx*activeS.vx + activeS.vy*activeS.vy + activeS.vz*activeS.vz;
            const r = Math.sqrt(activeS.x*activeS.x + activeS.y*activeS.y + activeS.z*activeS.z);
            const vMag = Math.sqrt(v2);
            const accMag = Math.sqrt(activeS.ax*activeS.ax + activeS.ay*activeS.ay + activeS.az*activeS.az);
            
            document.getElementById('calc-sub-pos').innerHTML = '&radic;( ('+activeS.x.toFixed(0)+')&sup2; + ('+activeS.y.toFixed(0)+')&sup2; + ('+activeS.z.toFixed(0)+')&sup2; )<br>= '+Math.round(r*1000).toLocaleString()+' km';
            document.getElementById('calc-sub-vel').innerHTML = '&radic;( ('+activeS.vx.toFixed(2)+')&sup2; + ('+activeS.vy.toFixed(2)+')&sup2; + ('+activeS.vz.toFixed(2)+')&sup2; )<br>= '+vMag.toFixed(2)+' km/s';
            document.getElementById('calc-sub-acc').innerHTML = 'a: ' + (accMag*100).toFixed(4) + ' m/s&sup2;<br>L: ' + activeS.arc.toLocaleString() + ' km';
            
            // Frenet-Serret
            const aT = (vMag > 0) ? ((activeS.vx*activeS.ax + activeS.vy*activeS.ay + activeS.vz*activeS.az) / vMag) : 0;
            const aN = Math.sqrt(Math.max(0, accMag*accMag - aT*aT));
            document.getElementById('calc-frenet').innerHTML = '|T| = 1<br>a_T (Tangent/Speed change) = '+(aT*100).toFixed(4)+' m/s&sup2;<br>a_N (Normal/Direction change) = '+(aN*100).toFixed(4)+' m/s&sup2;';

            // Jerk & Torsion (Live JS Calc)
            const jx = (activeS.ax - prevS.ax) / 0.1;
            const jy = (activeS.ay - prevS.ay) / 0.1;
            const jz = (activeS.az - prevS.az) / 0.1;
            
            const cx = activeS.vy*activeS.az - activeS.vz*activeS.ay;
            const cy = activeS.vz*activeS.ax - activeS.vx*activeS.az;
            const cz = activeS.vx*activeS.ay - activeS.vy*activeS.ax;
            const crossMagSq = cx*cx + cy*cy + cz*cz;
            
            let torsion = 0;
            if(crossMagSq > 1e-10) {{
                torsion = (cx*jx + cy*jy + cz*jz) / crossMagSq;
            }}
            document.getElementById('calc-torsion').innerHTML = 'j (Jerk Mag) = ' + (Math.sqrt(jx*jx+jy*jy+jz*jz)*100).toFixed(4) + ' m/s&sup3;<br>&tau; (Torsion) = ' + torsion.toExponential(4) + ' rad/km';

            // Work / Kinetic Energy
            const kineticEnergy = 0.5 * ORION_MASS * Math.pow(vMag * 1000, 2); 
            document.getElementById('calc-work').innerHTML = '&Delta;K = &frac12;mv&sup2;<br>= &frac12;(26500 kg)('+ (vMag*1000).toFixed(1) +' m/s)&sup2;<br>= ' + (kineticEnergy / 1e9).toFixed(2) + ' GJ (GigaJoules)';

            const eng = (v2 / 2) - (398.6 / r);
            document.getElementById('calc-eng').innerHTML = '&epsilon; = ('+vMag.toFixed(2)+')&sup2;/2 - 398.6/'+r.toFixed(1)+'<br>= ' + eng.toFixed(4) + ' km&sup2;/s&sup2;';
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
            const prevS = shipFrame > 0 ? shipData[Math.min(shipFrame-1, MAX - 1)] : activeS;

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
                    const r = Math.sqrt(activeS.x*activeS.x + activeS.y*activeS.y + activeS.z*activeS.z);
                    const vMag = Math.sqrt(activeS.vx*activeS.vx + activeS.vy*activeS.vy + activeS.vz*activeS.vz);
                    const dSM = Math.sqrt(Math.pow(currentMx-activeS.x,2) + Math.pow(currentMy-activeS.y,2) + Math.pow(currentMz-activeS.z,2)); 
                    
                    document.getElementById('hud-dist-earth').innerText = Math.round(r*1000).toLocaleString() + ' km';
                    document.getElementById('hud-dist-moon').innerText = Math.round(dSM*1000).toLocaleString() + ' km';
                    document.getElementById('hud-vel').innerText = vMag.toFixed(2) + ' km/s';
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
            }} else if(camMode === 'earth') {{
                const twLocalPos = new THREE.Vector3().setFromSphericalCoords(6.371 + 30, taipeiPhi, taipeiTheta);
                const twWorldPos = twLocalPos.applyAxisAngle(new THREE.Vector3(0,1,0), earth.rotation.y);
                camera.position.lerp(twWorldPos, 0.05);
                controls.target.lerp(new THREE.Vector3(activeS.x, activeS.y, activeS.z), 0.05);
            }} else if(camMode === 'ntut') {{
                const markerWorldPos = new THREE.Vector3();
                ntutMarker.getWorldPosition(markerWorldPos);
                
                const offset = markerWorldPos.clone().normalize().multiplyScalar(15);
                camTargetPos.copy(offset);
                
                camera.position.lerp(camTargetPos, 0.05);
                controls.target.lerp(markerWorldPos, 0.05);
                
                const s = 1 + Math.sin(Date.now() * 0.01) * 0.3;
                ntutRing.scale.set(s, s, 1);
            }} else if(camMode === 'ship' && !shipGroup.visible) {{
                setCamera('free'); 
            }}
            controls.update();

            if (isDesmos) {{
                updateCalculusHTML(activeS, prevS, currentMx, currentMy, currentMz);
                if (gMode === '2D') {{
                    const w = document.getElementById('desmos-grid').width;
                    const h = document.getElementById('desmos-grid').height;
                    const ox = w/2, oy = h/2; 
                    const sf = 0.65; 
                    
                    ctx2d.clearRect(0,0,w,h);
                    
                    ctx2d.strokeStyle = '#222'; ctx2d.lineWidth = 1;
                    for(let i=0; i<w; i+=40) {{ ctx2d.beginPath(); ctx2d.moveTo(i,0); ctx2d.lineTo(i,h); ctx2d.stroke(); }}
                    for(let i=0; i<h; i+=40) {{ ctx2d.beginPath(); ctx2d.moveTo(0,i); ctx2d.lineTo(w,i); ctx2d.stroke(); }}
                    
                    ctx2d.lineWidth = 1.5;
                    ctx2d.strokeStyle = '#ff5555'; ctx2d.beginPath(); ctx2d.moveTo(0,oy); ctx2d.lineTo(w,oy); ctx2d.stroke(); 
                    ctx2d.strokeStyle = '#00ff00'; ctx2d.beginPath(); ctx2d.moveTo(ox,0); ctx2d.lineTo(ox,h); ctx2d.stroke(); 
                    
                    ctx2d.fillStyle = '#ff5555'; ctx2d.font = 'bold 12px Consolas'; ctx2d.fillText('X 軸 (Axis)', w-70, oy-10);
                    ctx2d.fillStyle = '#00ff00'; ctx2d.fillText('Y 軸 (Axis)', ox+10, 20);
                    
                    ctx2d.fillStyle = '#1a73e8'; ctx2d.beginPath(); ctx2d.arc(ox, oy, 8, 0, 7); ctx2d.fill(); 
                    ctx2d.fillStyle = '#aaa'; ctx2d.beginPath(); ctx2d.arc(ox + currentMx*sf, oy - currentMy*sf, 5, 0, 7); ctx2d.fill(); 
                    
                    const px = ox + activeS.x*sf, py = oy - activeS.y*sf;
                    ctx2d.fillStyle = '#fff'; ctx2d.beginPath(); ctx2d.arc(px, py, 3, 0, 7); ctx2d.fill(); 
                    
                    ctx2d.strokeStyle = '#00e5ff'; ctx2d.lineWidth = 2; ctx2d.beginPath(); ctx2d.moveTo(px,py); ctx2d.lineTo(px + activeS.vx*5, py - activeS.vy*5); ctx2d.stroke();
                    
                    const visualAx = activeS.ax*5000; const visualAy = activeS.ay*5000;
                    let accLen = Math.sqrt(visualAx*visualAx + visualAy*visualAy);
                    let scaleA = accLen > 150 ? 150/accLen : 1; 
                    ctx2d.strokeStyle = '#ff5555'; ctx2d.lineWidth = 2; ctx2d.beginPath(); ctx2d.moveTo(px,py); ctx2d.lineTo(px + visualAx*scaleA, py - visualAy*scaleA); ctx2d.stroke();
                    
                    ctx2d.fillStyle = '#fff'; ctx2d.font = '12px Consolas';
                    ctx2d.fillText('Ship(x:'+activeS.x.toFixed(0)+', y:'+activeS.y.toFixed(0)+')', px+10, py-10);
                    
                    // Hide 3D labels when in 2D mode
                    update3DLabel('hud-3d-ship', new THREE.Vector3(), false);
                    update3DLabel('hud-3d-x', new THREE.Vector3(), false);
                    update3DLabel('hud-3d-y', new THREE.Vector3(), false);
                    update3DLabel('hud-3d-z', new THREE.Vector3(), false);
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
                        accArrow.setLength(Math.min(aDir.length() * 10000, 50), 10, 5);
                        accArrow.position.copy(subShip.position);
                    }}
                    
                    // Update Dynamic 3D Labels
                    document.getElementById('hud-3d-ship').innerText = 'Ship (x: ' + activeS.x.toFixed(0) + ', y: ' + activeS.y.toFixed(0) + ', z: ' + activeS.z.toFixed(0) + ')';
                    update3DLabel('hud-3d-ship', subShip.position, true);
                    update3DLabel('hud-3d-x', new THREE.Vector3(150,0,0), true);
                    update3DLabel('hud-3d-y', new THREE.Vector3(0,150,0), true);
                    update3DLabel('hud-3d-z', new THREE.Vector3(0,0,150), true);
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

filename = "artemis2_calculus_masterpiece.html"
with open(filename, "w", encoding="utf-8") as f:
    f.write(html_content)

webbrowser.open('file://' + os.path.realpath(filename))
print("✅ Artemis II Calculus Master Simulator is Ready with Perfect 3D HUD Tracking!")