-- LEVI Hub - Final Build with Smart Multi-Layer Scan Engine
local SoundService = game:GetService("SoundService")
local Players = game:GetService("Players")
local CollectionService = game:GetService("CollectionService")
local RunService = game:GetService("RunService")
local LocalPlayer = Players.LocalPlayer

-- وظيفة تشغيل صوت تنبيه عند بدء تشغيل السكربت
local function PlayIntroSound()
    local sound = Instance.new("Sound")
    sound.SoundId = "rbxassetid://4590662766" 
    sound.Volume = 1.0
    sound.Parent = LocalPlayer:WaitForChild("PlayerGui")
    sound:Play()
    
    sound.Ended:Connect(function()
        sound:Destroy()
    end)
end

PlayIntroSound()

local Fluent = loadstring(game:HttpGet("https://github.com/dawid-scripts/Fluent/releases/latest/download/main.lua"))()
local SaveManager = loadstring(game:HttpGet("https://raw.githubusercontent.com/dawid-scripts/Fluent/master/Addons/SaveManager.lua"))()
local InterfaceManager = loadstring(game:HttpGet("https://raw.githubusercontent.com/dawid-scripts/Fluent/master/Addons/InterfaceManager.lua"))()

local Window = Fluent:CreateWindow({
    Title = "LEVI Hub",
    SubTitle = "",
    TabWidth = 130,
    Size = UDim2.fromOffset(450, 320),
    Theme = "Dark",
    MinimizeKey = Enum.KeyCode.LeftControl
})

local Tabs = {
    ESP = Window:AddTab({ Title = "ESP", Icon = "scan-eye" })
}

Fluent:Notify({
    Title = "LEVI HUB",
    Content = "Welcome back, " .. LocalPlayer.Name .. "!",
    SubContent = "LEVI Hub Loaded Successfully.",
    Duration = 5
})

local ToggleGui = Instance.new("ScreenGui", game:GetService("CoreGui"))
ToggleGui.Name = "LEVIHubMobileToggle"
ToggleGui.ResetOnSpawn = false

local OpenButton = Instance.new("ImageButton", ToggleGui)
OpenButton.Size = UDim2.new(0, 50, 0, 50)
OpenButton.Position = UDim2.new(0, 15, 0, 200)
OpenButton.BackgroundColor3 = Color3.fromRGB(10, 10, 10)
OpenButton.ScaleType = Enum.ScaleType.Fit
OpenButton.Draggable = true

local UICorner = Instance.new("UICorner", OpenButton)
UICorner.CornerRadius = UDim.new(1, 0)
local UIStroke = Instance.new("UIStroke", OpenButton)
UIStroke.Color = Color3.fromRGB(200, 200, 200)
UIStroke.Thickness = 1.5

OpenButton.Image = "rbxthumb://type=Asset&id=125736334820526&w=150&h=150"

OpenButton.MouseButton1Click:Connect(function()
    Window:Minimize()
end)

---------------------------------------------------------
-- ⚡ محرك الكشف الخارق والذكي (منع التكرار والتداخل)
---------------------------------------------------------
local function scanEntity(model)
    if not model or not model:IsA("Model") then return nil, nil end
    if model == LocalPlayer.Character then return nil, nil end

    -- منع فحص الموديلات الفرعية إذا كان الأب (Parent) موديل يحتوي على Humanoid لمنع التكرار
    if model.Parent and model.Parent:IsA("Model") and model.Parent:FindFirstChildOfClass("Humanoid") then
        return nil, nil
    end

    local hum = model:FindFirstChildOfClass("Humanoid")
    if not hum or hum.Health <= 0 then return nil, nil end

    -- 1️⃣ كشف اللاعبين الحقيقيين (أصدقائك في السيرفر)
    local targetPlayer = Players:GetPlayerFromCharacter(model) or Players:FindFirstChild(model.Name)
    if targetPlayer then
        return "PLAYER: " .. targetPlayer.DisplayName, Color3.fromRGB(255, 215, 0)
    end

    local nameLower = string.lower(model.Name)

    -- 2️⃣ فحص الطاقم الطبي والأطباء
    if nameLower:find("doctor") or nameLower:find("staff") or nameLower:find("nurse") or nameLower:find("guard") then 
        return "Doctor", Color3.fromRGB(0, 190, 255) 
    end

    local isAnomaly = false

    -- 3️⃣ فحص الخصائص المخفية والديناميكية (Attributes Deep Scan)
    for key, val in pairs(model:GetAttributes()) do
        local keyLower = string.lower(key)
        if keyLower:find("anomaly") or keyLower:find("mutat") or keyLower:find("infect") or keyLower:find("fake") or keyLower:find("monster") or keyLower:find("evil") then
            isAnomaly = true
            break
        end
        if typeof(val) == "boolean" and val == true then
            if keyLower:find("bad") or keyLower:find("hostile") or keyLower:find("anomaly") then
                isAnomaly = true
                break
            end
        end
    end

    -- 4️⃣ فحص العلامات والنماذج البرمجية (CollectionService Tags)
    if not isAnomaly then
        for _, tag in ipairs(CollectionService:GetTags(model)) do
            local tagLower = string.lower(tag)
            if tagLower:find("anomaly") or tagLower:find("monster") or tagLower:find("infected") or tagLower:find("mutated") then
                isAnomaly = true
                break
            end
        end
    end

    -- 5️⃣ فحص الأسماء والـ Hierarchy Tree
    if not isAnomaly then
        if nameLower:find("anomaly") or nameLower:find("mutated") or nameLower:find("infected") or nameLower:find("monster") or nameLower:find("fake") or nameLower:find("alternate") then
            isAnomaly = true
        end
    end

    -- 6️⃣ فحص المكونات الداخلية الهيكلية
    if not isAnomaly then
        for _, child in ipairs(model:GetChildren()) do
            local cName = string.lower(child.Name)
            if cName:find("anomaly") or cName:find("infect") or cName:find("glitch") or cName:find("distortion") then
                isAnomaly = true
                break
            end
        end
    end

    -- 7️⃣ فحص التشوهات الفيزيائية
    if not isAnomaly then
        local head = model:FindFirstChild("Head")
        local hrp = model:FindFirstChild("HumanoidRootPart")
        if head and hrp then
            local headSize = head.Size.Magnitude
            if headSize > 4.5 or headSize < 0.5 then
                isAnomaly = true
            end
        end
    end

    if isAnomaly then 
        return "ANOMALY", Color3.fromRGB(255, 35, 35) 
    end

    return "Normal", Color3.fromRGB(0, 255, 120)
end

---------------------------------------------------------
-- 👁️ نظام العرض والرؤية عبر الجدران
---------------------------------------------------------
local function applySmartESP(obj)
    if not obj or not obj:IsA("Model") or obj == LocalPlayer.Character then return end
    
    local status, color = scanEntity(obj)
    
    -- إذا كان الكائن لا ينطبق عليه الفحص أو تم إزالته، نحذف النصوص القديمة
    if not status then 
        if obj:FindFirstChild("LEVI_ESP") then obj.LEVI_ESP:Destroy() end
        if obj:FindFirstChild("LEVI_Highlight") then obj.LEVI_Highlight:Destroy() end
        return 
    end

    local hrp = obj:FindFirstChild("HumanoidRootPart") or obj:FindFirstChild("Head") or obj.PrimaryPart
    if not hrp then return end

    -- 1. إنشاء أو تحديث نص الـ ESP
    local espGui = obj:FindFirstChild("LEVI_ESP")
    if not espGui then
        espGui = Instance.new("BillboardGui")
        espGui.Name = "LEVI_ESP"
        espGui.Size = UDim2.new(0, 100, 0, 20)
        espGui.AlwaysOnTop = true
        espGui.StudsOffset = Vector3.new(0, 2.4, 0)
        espGui.Adornee = hrp
        espGui.Parent = obj

        local txt = Instance.new("TextLabel", espGui)
        txt.Name = "Label"
        txt.Size = UDim2.new(1, 0, 1, 0)
        txt.BackgroundTransparency = 1
        txt.TextSize = 12
        txt.Font = Enum.Font.GothamBold
        txt.TextStrokeTransparency = 0
        txt.TextStrokeColor3 = Color3.fromRGB(0, 0, 0)
    end

    local label = espGui:FindFirstChild("Label")
    if label then
        label.Text = status
        label.TextColor3 = color
    end

    -- 2. إنشاء وتحديث التوهج (Highlight)
    local highlight = obj:FindFirstChild("LEVI_Highlight")
    if not highlight then
        highlight = Instance.new("Highlight")
        highlight.Name = "LEVI_Highlight"
        highlight.DepthMode = Enum.HighlightDepthMode.AlwaysOnTop
        highlight.FillTransparency = 0.5
        highlight.OutlineTransparency = 0.1
        highlight.Parent = obj
    end
    highlight.FillColor = color
    highlight.OutlineColor = color
end

-- قسم NPC Labels
Tabs.ESP:AddSection("NPC Labels")

local ESPToggle = Tabs.ESP:AddToggle("EnableNPCESP", {
    Title = "Enable NPC ESP",
    Description = "Shows Enemy / Normal / Anomaly labels\nabove NPCs",
    Default = false
})

ESPToggle:OnChanged(function(v)
    if v then
        Fluent:Notify({
            Title = "LEVI HUB",
            Content = "تم تفعيل بنجاح",
            Duration = 3
        })

        task.spawn(function()
            while Fluent.Options.EnableNPCESP.Value do
                task.wait(0.2)
                for _, obj in ipairs(workspace:GetDescendants()) do
                    if obj:IsA("Model") and obj:FindFirstChildOfClass("Humanoid") then
                        applySmartESP(obj)
                    end
                end
            end
        end)
    else
        Fluent:Notify({
            Title = "LEVI HUB",
            Content = "تم إيقاف التفعيل بنجاح",
            Duration = 3
        })

        for _, obj in ipairs(workspace:GetDescendants()) do 
            if obj.Name == "LEVI_ESP" then obj:Destroy() end 
            if obj.Name == "LEVI_Highlight" then obj:Destroy() end
        end
    end
end)

Window:SelectTab(1)
