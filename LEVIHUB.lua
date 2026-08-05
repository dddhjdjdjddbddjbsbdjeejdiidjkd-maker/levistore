-- =================================================================
--        LEVI HUB - Blox Fruits Complete Integrated Script
-- =================================================================

local Players = game:GetService("Players")
local RunService = game:GetService("RunService")
local TweenService = game:GetService("TweenService")
local ReplicatedStorage = game:GetService("ReplicatedStorage")
local Workspace = game:GetService("Workspace")
local SoundService = game:GetService("SoundService")
local VirtualUser = game:GetService("VirtualUser")
local CoreGui = game:GetService("CoreGui")
local VirtualInputManager = game:GetService("VirtualInputManager")

local LocalPlayer = Players.LocalPlayer

-- -----------------------------------------------------------------
-- 🔊 1. صوت الترحيب
-- -----------------------------------------------------------------
pcall(function()
    local StartSound = Instance.new("Sound")
    StartSound.SoundId = "rbxassetid://4590662766"
    StartSound.Volume = 1.5
    StartSound.Parent = SoundService
    StartSound:Play()
end)

local function PlayActivationSound()
    pcall(function()
        local sound = Instance.new("Sound")
        sound.SoundId = "rbxassetid://4590662766"
        sound.Volume = 1.0
        sound.Parent = SoundService
        sound:Play()
        sound.Ended:Connect(function() sound:Destroy() end)
    end)
end

-- -----------------------------------------------------------------
-- 🛡️ 2. الحماية ضد الـ AFK
-- -----------------------------------------------------------------
LocalPlayer.Idled:Connect(function()
    VirtualUser:Button2Down(Vector2.new(0,0), workspace.CurrentCamera.CFrame)
    task.wait(1)
    VirtualUser:Button2Up(Vector2.new(0,0), workspace.CurrentCamera.CFrame)
end)

-- -----------------------------------------------------------------
-- 🔘 3. زر (LEVI)
-- -----------------------------------------------------------------
local ScreenGui = Instance.new("ScreenGui")
local ToggleButton = Instance.new("TextButton")
local UICorner = Instance.new("UICorner")
local UIStroke = Instance.new("UIStroke")

ScreenGui.Name = "LEVI_ToggleUI"
ScreenGui.Parent = CoreGui or LocalPlayer:WaitForChild("PlayerGui")
ScreenGui.ResetOnSpawn = false

ToggleButton.Name = "LEVI_Btn"
ToggleButton.Parent = ScreenGui
ToggleButton.Size = UDim2.new(0, 90, 0, 45)
ToggleButton.Position = UDim2.new(0.05, 0, 0.15, 0)
ToggleButton.BackgroundColor3 = Color3.fromRGB(15, 15, 15)
ToggleButton.Text = "LEVI"
ToggleButton.TextColor3 = Color3.fromRGB(50, 160, 255)
ToggleButton.TextSize = 20
ToggleButton.Font = Enum.Font.SourceSansBold
ToggleButton.Active = true
ToggleButton.Draggable = true

UICorner.CornerRadius = UDim.new(0, 12)
UICorner.Parent = ToggleButton

UIStroke.Parent = ToggleButton
UIStroke.Color = Color3.fromRGB(35, 35, 35)
UIStroke.Thickness = 2

ToggleButton.MouseButton1Click:Connect(function()
    PlayActivationSound()
    VirtualInputManager:SendKeyEvent(true, Enum.KeyCode.LeftControl, false, game)
    VirtualInputManager:SendKeyEvent(false, Enum.KeyCode.LeftControl, false, game)
end)

-- -----------------------------------------------------------------
-- ⚙️ 4. الإعدادات والريموتات
-- -----------------------------------------------------------------
local CommF = ReplicatedStorage:FindFirstChild("CommF_", true) or ReplicatedStorage:WaitForChild("Remotes"):WaitForChild("CommF_")
local Net = ReplicatedStorage:FindFirstChild("RE/RegisterAttack", true) and ReplicatedStorage:FindFirstChild("Modules"):FindFirstChild("Net") or ReplicatedStorage:WaitForChild("Modules"):WaitForChild("Net")
local RegisterAttack = Net:WaitForChild("RE/RegisterAttack")
local RegisterHit = Net:WaitForChild("RE/RegisterHit")

local Settings = {
    AutoFarm = false,
    AutoEquip = true,
    FastAttack = true,
    SelectedWeapon = "Melee",
    HeightOffset = 5.5,
    BackOffset = -1.0,
    TweenSpeed = 350,
    BurstHits = 10,
    AttackDistance = 120,
    
    AutoStoreFruit = false,
    TeleportToFruitSpawn = false
}

local LevelData = {
    { Min = 1,    Max = 9,    Mob = "Bandit",             Quest = "BanditQuest1",     QuestLvl = 1, NpcCFrame = CFrame.new(1059, 16, 1550),  MobCFrame = CFrame.new(1145, 17, 1634) },
    { Min = 10,   Max = 14,   Mob = "Monkey",             Quest = "JungleQuest",      QuestLvl = 1, NpcCFrame = CFrame.new(-1598, 37, 153),  MobCFrame = CFrame.new(-1448, 50, 63) },
    { Min = 15,   Max = 29,   Mob = "Gorilla",            Quest = "JungleQuest",      QuestLvl = 2, NpcCFrame = CFrame.new(-1598, 37, 153),  MobCFrame = CFrame.new(-1237, 6, -486) },
    { Min = 30,   Max = 39,   Mob = "Pirate",             Quest = "BuggyQuest1",      QuestLvl = 1, NpcCFrame = CFrame.new(-1140, 4, 3828),  MobCFrame = CFrame.new(-1115, 14, 3938) },
    { Min = 40,   Max = 59,   Mob = "Brute",              Quest = "BuggyQuest1",      QuestLvl = 2, NpcCFrame = CFrame.new(-1140, 4, 3828),  MobCFrame = CFrame.new(-1145, 14, 4308) },
    { Min = 60,   Max = 89,   Mob = "Desert Bandit",      Quest = "DesertQuest",      QuestLvl = 1, NpcCFrame = CFrame.new(894, 6, 4388),    MobCFrame = CFrame.new(982, 16, 4405) },
    { Min = 90,   Max = 119,  Mob = "Snow Bandit",        Quest = "SnowQuest",        QuestLvl = 1, NpcCFrame = CFrame.new(1386, 87, -1298), MobCFrame = CFrame.new(1287, 105, -1380) },
    { Min = 120,  Max = 149,  Mob = "Chief Petty Officer",Quest = "MarineQuest2",     QuestLvl = 1, NpcCFrame = CFrame.new(-5030, 28, 4322), MobCFrame = CFrame.new(-4800, 21, 4260) },
    { Min = 150,  Max = 174,  Mob = "Sky Bandit",         Quest = "SkyQuest",         QuestLvl = 1, NpcCFrame = CFrame.new(-4840, 717, -2620),MobCFrame = CFrame.new(-4975, 714, -2880) },
    { Min = 175,  Max = 224,  Mob = "Dark Master",        Quest = "SkyQuest",         QuestLvl = 2, NpcCFrame = CFrame.new(-4840, 717, -2620),MobCFrame = CFrame.new(-5220, 388, -2250) },
    { Min = 225,  Max = 299,  Mob = "Toga Warrior",       Quest = "ColosseumQuest",   QuestLvl = 1, NpcCFrame = CFrame.new(-1580, 7, -2980), MobCFrame = CFrame.new(-1800, 50, -2750) },
    { Min = 300,  Max = 374,  Mob = "Military Soldier",   Quest = "MagmaQuest",       QuestLvl = 1, NpcCFrame = CFrame.new(-5310, 12, 8515),  MobCFrame = CFrame.new(-5400, 60, 8450) },
    { Min = 375,  Max = 449,  Mob = "Fishman Warrior",    Quest = "FishmanQuest",     QuestLvl = 1, NpcCFrame = CFrame.new(61122, 18, 1568), MobCFrame = CFrame.new(60800, 18, 1500) },
    { Min = 450,  Max = 524,  Mob = "God's Guard",        Quest = "UpperSkyQuest1",   QuestLvl = 1, NpcCFrame = CFrame.new(-4608, 845, -1912),MobCFrame = CFrame.new(-4700, 845, -1900) },
    { Min = 525,  Max = 624,  Mob = "Royal Squad",        Quest = "UpperSkyQuest2",   QuestLvl = 1, NpcCFrame = CFrame.new(-7900, 5611, -2280),MobCFrame = CFrame.new(-7700, 5600, -2200) },
    { Min = 625,  Max = 699,  Mob = "Galley Pirate",      Quest = "FountainQuest",    QuestLvl = 1, NpcCFrame = CFrame.new(5258, 38, 4050),   MobCFrame = CFrame.new(5500, 38, 3950) },
    { Min = 700,  Max = 2800, Mob = "Raider",             Quest = "Area1Quest",       QuestLvl = 1, NpcCFrame = CFrame.new(-425, 73, 1835),   MobCFrame = CFrame.new(-500, 73, 1600) }
}

-- -----------------------------------------------------------------
-- 🎨 5. الواجهة Fluent UI
-- -----------------------------------------------------------------
local Fluent = loadstring(game:HttpGet("https://github.com/dawid-scripts/Fluent/releases/latest/download/main.lua"))()

local Window = Fluent:CreateWindow({
    Title = "LEVI HUB",
    SubTitle = "Blox Fruits | By LEVI",
    TabWidth = 160,
    Size = UDim2.fromOffset(580, 380),
    Acrylic = false,
    Theme = "Darker",
    MinimizeKey = Enum.KeyCode.LeftControl
})

local Tabs = {
    Info     = Window:AddTab({ Title = "Information", Icon = "info" }),
    AutoFarm = Window:AddTab({ Title = "Auto Farm", Icon = "sword" }),
    Fruits   = Window:AddTab({ Title = "Fruits", Icon = "apple" })
}

Tabs.Info:AddSection("Information ℹ️")
Tabs.Info:AddParagraph({
    Title = "مرحبا بكم ⚔️",
    Content = "مرحبا بكم في سكربت بلوكس فروت للحصول علي المزيد من سكربتات عليك الانضمام الي جروب تلجرام:\nhttps://t.me/levimod6"
})

Tabs.Info:AddButton({
    Title = "نسخ رابط التلجرام",
    Callback = function()
        PlayActivationSound()
        setclipboard("https://t.me/levimod6")
        Fluent:Notify({ Title = "تم النسخ", Content = "تم نسخ رابط التلجرام!", Duration = 3 })
    end
})

Tabs.AutoFarm:AddSection("Auto Farm ⚔️")
local WeaponDropdown = Tabs.AutoFarm:AddDropdown("SelectWeapon", {
    Title = "Select Weapon",
    Values = {"Melee", "Sword", "Blox Fruit"},
    Multi = false,
    Default = 1,
})
WeaponDropdown:OnChanged(function(Value) Settings.SelectedWeapon = Value end)

local AutoFarmToggle = Tabs.AutoFarm:AddToggle("AutoFarmLevel", { Title = "Auto Farm Level", Default = false })
AutoFarmToggle:OnChanged(function(Value) Settings.AutoFarm = Value end)

local FastAttackToggle = Tabs.AutoFarm:AddToggle("FastAttack", { Title = "Fast Attack", Default = true })
FastAttackToggle:OnChanged(function(Value) Settings.FastAttack = Value end)

-- 🔍 كشف بائع الفواكه العشوائية (Blox Fruit Gacha)
local function GetFruitDealerCFrame()
    local searchKeywords = {"gacha", "cousin", "zioles", "blox fruit dealer"}
    for _, obj in ipairs(Workspace:GetDescendants()) do
        if obj:IsA("Model") then
            local lowerName = string.lower(obj.Name)
            for _, key in ipairs(searchKeywords) do
                if string.find(lowerName, key) then
                    local hrp = obj:FindFirstChild("HumanoidRootPart") or obj.PrimaryPart or obj:FindFirstChild("Head")
                    if hrp then return hrp.CFrame end
                end
            end
        end
    end

    local pId = game.PlaceId
    if pId == 2753915549 then
        return CFrame.new(-1612, 37.8, 149) -- Sea 1
    elseif pId == 4442272183 then
        return CFrame.new(-28.5, 73, -3001) -- Sea 2
    elseif pId == 7449423635 then
        return CFrame.new(-1254.3, 337.2, -7470) -- Sea 3
    end
    return nil
end

local function DirectBuyFruit()
    local result = nil
    pcall(function() result = CommF:InvokeServer("Cousin", "Buy") end)
    if not result then
        pcall(function() result = CommF:InvokeServer("Cousin", "Buy", "Random") end)
    end
    return result
end

-- -----------------------------------------------------------------
-- 🍎 6. قسم Fruits
-- -----------------------------------------------------------------
Tabs.Fruits:AddSection("Fruits")

local isBuyingFruitInProcess = false
Tabs.Fruits:AddButton({
    Title = "Teleport to Fruit Dealer 🏪",
    Callback = function()
        if isBuyingFruitInProcess then return end
        isBuyingFruitInProcess = true
        PlayActivationSound()

        local dealerCFrame = GetFruitDealerCFrame()
        if dealerCFrame then
            Fluent:Notify({ Title = "Fruit Dealer 🏪", Content = "جاري الانتقال لمنصة Blox Fruit Gacha...", Duration = 3 })
            
            local hrp = LocalPlayer.Character and LocalPlayer.Character:FindFirstChild("HumanoidRootPart")
            if hrp then
                local noCollide = RunService.Stepped:Connect(function()
                    if LocalPlayer.Character then
                        for _, part in ipairs(LocalPlayer.Character:GetChildren()) do
                            if part:IsA("BasePart") then part.CanCollide = false end
                        end
                    end
                end)

                local targetCFrame = dealerCFrame * CFrame.new(0, 0, 3)
                local dist = (hrp.Position - targetCFrame.Position).Magnitude
                local tween = TweenService:Create(hrp, TweenInfo.new(dist / Settings.TweenSpeed, Enum.EasingStyle.Linear), {CFrame = targetCFrame})

                tween:Play()
                tween.Completed:Wait()
                noCollide:Disconnect()
                hrp.AssemblyLinearVelocity = Vector3.new(0, 0, 0)

                task.wait(0.3)
                local res = DirectBuyFruit()

                if res then
                    if typeof(res) == "Instance" then
                        Fluent:Notify({ Title = "Gacha Fruit 🍎", Content = "مبروك! حصلت على: " .. res.Name, Duration = 6 })
                    elseif typeof(res) == "string" then
                        Fluent:Notify({ Title = "Gacha Fruit 🍎", Content = tostring(res), Duration = 5 })
                    else
                        Fluent:Notify({ Title = "Gacha Fruit 🍎", Content = "تمت عملية الشراء بنجاح!", Duration = 5 })
                    end
                else
                    Fluent:Notify({ Title = "Gacha Fruit ⚠️", Content = "تعذر الشراء (تأكد من وجود فلوس كافية أو انقضاء وقت الـ Cooldown)", Duration = 5 })
                end
            end
        else
            Fluent:Notify({ Title = "Fruit Dealer ⚠️", Content = "تعذر تحديد موقع البائع في هذه الخريطة!", Duration = 4 })
        end

        isBuyingFruitInProcess = false
    end
})

-- Auto Store Fruits
local AutoStoreToggle = Tabs.Fruits:AddToggle("AutoStoreFruits", { Title = "Auto Store Fruits", Default = false })
AutoStoreToggle:OnChanged(function(Value)
    PlayActivationSound()
    Settings.AutoStoreFruit = Value
    Fluent:Notify({ Title = "Fruits", Content = "Auto Store Fruits: " .. (Value and "تم التفعيل ✅" or "تم الإيقاف ❌"), Duration = 3 })
end)

-- Teleport To Fruit Spawn
local TeleportFruitSpawnToggle = Tabs.Fruits:AddToggle("TeleportToFruitSpawn", { Title = "Teleport To Fruit Spawn", Default = false })
TeleportFruitSpawnToggle:OnChanged(function(Value)
    PlayActivationSound()
    Settings.TeleportToFruitSpawn = Value
    if Value then
        Fluent:Notify({ Title = "Fruits 🍎", Content = "تم تفعيل التلبرت الآمن للفواكه", Duration = 3 })
    end
end)

-- -----------------------------------------------------------------
-- 🚀 7. المحركات والوظائف
-- -----------------------------------------------------------------

-- NoClip
RunService.Stepped:Connect(function()
    if (Settings.AutoFarm or Settings.TeleportToFruitSpawn) and LocalPlayer.Character then
        for _, part in ipairs(LocalPlayer.Character:GetChildren()) do
            if part:IsA("BasePart") then part.CanCollide = false end
        end
    end
end)

-- Equip Weapon
local function EquipWeapon()
    local char = LocalPlayer.Character
    if not char or not char:FindFirstChild("Humanoid") then return end
    local backpack = LocalPlayer:FindFirstChild("Backpack")
    if not backpack then return end

    local currentTool = char:FindFirstChildOfClass("Tool")
    if currentTool then
        if Settings.SelectedWeapon == "Melee" and currentTool.ToolTip == "Melee" then return end
        if Settings.SelectedWeapon == "Sword" and currentTool.ToolTip == "Sword" then return end
        if Settings.SelectedWeapon == "Blox Fruit" and currentTool.ToolTip == "Blox Fruit" then return end
    end

    for _, tool in ipairs(backpack:GetChildren()) do
        if tool:IsA("Tool") and tool.ToolTip == Settings.SelectedWeapon then
            char.Humanoid:EquipTool(tool)
            return
        end
    end
end

-- Get Level Data
local function GetCurrentData()
    if not LocalPlayer:FindFirstChild("Data") or not LocalPlayer.Data:FindFirstChild("Level") then return LevelData[1] end
    local pLevel = LocalPlayer.Data.Level.Value
    for _, data in ipairs(LevelData) do
        if pLevel >= data.Min and pLevel <= data.Max then return data end
    end
    return LevelData[#LevelData]
end

local function HasQuest()
    local mainGui = LocalPlayer.PlayerGui:FindFirstChild("Main")
    return mainGui and mainGui:FindFirstChild("Quest") and mainGui.Quest.Visible
end

local currentTween = nil
local lastTargetPosition = nil
local function CancelTween()
    if currentTween then currentTween:Cancel() currentTween = nil lastTargetPosition = nil end
end

local function SafeTravel(targetCFrame)
    local hrp = LocalPlayer.Character and LocalPlayer.Character:FindFirstChild("HumanoidRootPart")
    if not hrp then return false end
    local dist = (hrp.Position - targetCFrame.Position).Magnitude
    if dist < 12 then CancelTween() hrp.CFrame = targetCFrame return true end

    if not currentTween or lastTargetPosition ~= targetCFrame.Position then
        CancelTween()
        lastTargetPosition = targetCFrame.Position
        currentTween = TweenService:Create(hrp, TweenInfo.new(dist / Settings.TweenSpeed, Enum.EasingStyle.Linear), {CFrame = targetCFrame})
        currentTween:Play()
    end
    return false
end

local function GetClosestTarget(mobName)
    local enemies = Workspace:FindFirstChild("Enemies") or Workspace
    local closestMob = nil
    local shortestDist = math.huge
    local hrp = LocalPlayer.Character and LocalPlayer.Character:FindFirstChild("HumanoidRootPart")
    if not hrp then return nil end

    for _, mob in ipairs(enemies:GetChildren()) do
        if mob:FindFirstChild("Humanoid") and mob:FindFirstChild("HumanoidRootPart") and mob.Humanoid.Health > 0 and string.find(mob.Name, mobName) then
            local dist = (hrp.Position - mob.HumanoidRootPart.Position).Magnitude
            if dist < shortestDist then shortestDist = dist closestMob = mob end
        end
    end
    return closestMob
end

-- Fast Attack Loop
task.spawn(function()
    while true do
        task.wait(0.015)
        if Settings.FastAttack then
            local char = LocalPlayer.Character
            if char and char:FindFirstChild("HumanoidRootPart") then
                if Settings.AutoEquip and not char:FindFirstChildOfClass("Tool") then EquipWeapon() end
                local tool = char:FindFirstChildOfClass("Tool")
                if tool then
                    pcall(function()
                        local enemies = Workspace:FindFirstChild("Enemies") or Workspace
                        local closestTarget = nil
                        local shortestDist = Settings.AttackDistance
                        for _, mob in ipairs(enemies:GetChildren()) do
                            local hum = mob:FindFirstChild("Humanoid")
                            local hrp = mob:FindFirstChild("HumanoidRootPart")
                            if hum and hrp and hum.Health > 0 then
                                local dist = (char.HumanoidRootPart.Position - hrp.Position).Magnitude
                                if dist <= shortestDist then shortestDist = dist closestTarget = hrp end
                            end
                        end
                        if closestTarget then
                            tool:Activate()
                            for i = 1, Settings.BurstHits do
                                RegisterAttack:FireServer(0)
                                RegisterHit:FireServer(closestTarget, {closestTarget})
                            end
                        end
                    end)
                end
            end
        end
    end
end)

-- 📦 نظام تخزين الفواكه الشامل المطور
local function UniversalStoreFruit(tool)
    if not tool or not tool:IsA("Tool") then return end
    
    local toolName = tool.Name
    local toolLower = string.lower(toolName)

    local isFruit = string.find(toolLower, "fruit") 
        or tool.ToolTip == "Blox Fruit" 
        or tool:FindFirstChild("Fruit")
        or (tool:FindFirstChild("Handle") and tool:FindFirstChild("Data"))

    if not isFruit then return end

    local cleanName = string.gsub(toolName, " [Ff]ruit", "")
    cleanName = string.gsub(cleanName, " Fruit", "")
    cleanName = string.gsub(cleanName, " ", "")

    local doubleFormat = cleanName .. "-" .. cleanName

    local formatsToTry = {
        doubleFormat,
        cleanName,
        toolName,
        toolName .. " Fruit"
    }

    if tool:GetAttribute("OriginalName") then
        table.insert(formatsToTry, tool:GetAttribute("OriginalName"))
    end

    for _, fruitId in ipairs(formatsToTry) do
        pcall(function() CommF:InvokeServer("StoreFruit", fruitId, tool) end)
        pcall(function() CommF:InvokeServer("StoreFruit", fruitId) end)
    end
end

task.spawn(function()
    while task.wait(0.8) do
        if Settings.AutoStoreFruit then
            pcall(function()
                local backpack = LocalPlayer:FindFirstChild("Backpack")
                local char = LocalPlayer.Character

                if backpack then
                    for _, tool in ipairs(backpack:GetChildren()) do
                        UniversalStoreFruit(tool)
                    end
                end

                if char then
                    for _, tool in ipairs(char:GetChildren()) do
                        UniversalStoreFruit(tool)
                    end
                end
            end)
        end
    end
end)

-- Fruit Teleport Loop
local isTeleportingFruit = false
task.spawn(function()
    while task.wait(1) do
        if Settings.TeleportToFruitSpawn and not isTeleportingFruit then
            pcall(function()
                local hrp = LocalPlayer.Character and LocalPlayer.Character:FindFirstChild("HumanoidRootPart")
                if not hrp then return end

                local targetFruit = nil
                local shortestDist = math.huge

                for _, object in ipairs(Workspace:GetChildren()) do
                    if (object:IsA("Tool") or object:IsA("Model")) and string.find(string.lower(object.Name), "fruit") then
                        local fruitPart = object:FindFirstChild("Handle") or object:FindFirstChildOfClass("BasePart")
                        if fruitPart then
                            local dist = (hrp.Position - fruitPart.Position).Magnitude
                            if dist < shortestDist then shortestDist = dist targetFruit = fruitPart end
                        end
                    end
                end

                if targetFruit then
                    isTeleportingFruit = true
                    Fluent:Notify({ Title = "Fruits 🍎", Content = "جاري الذهاب للفاكهة بالطيران الآمن...", Duration = 3 })

                    local targetCFrame = targetFruit.CFrame * CFrame.new(0, 2, 0)
                    local dist = (hrp.Position - targetCFrame.Position).Magnitude
                    local tween = TweenService:Create(hrp, TweenInfo.new(dist / Settings.TweenSpeed, Enum.EasingStyle.Linear), {CFrame = targetCFrame})

                    tween:Play()
                    tween.Completed:Wait()

                    hrp.AssemblyLinearVelocity = Vector3.new(0, 0, 0)
                    task.wait(0.5)
                    isTeleportingFruit = false
                end
            end)
        end
    end
end)

-- Main Auto Farm Loop
task.spawn(function()
    while task.wait(0.01) do
        if Settings.AutoFarm and not isTeleportingFruit and not isBuyingFruitInProcess then
            local char = LocalPlayer.Character
            local hrp = char and char:FindFirstChild("HumanoidRootPart")
            if hrp then
                local currentData = GetCurrentData()
                if not HasQuest() then
                    local reachedNPC = SafeTravel(currentData.NpcCFrame * CFrame.new(0, 15, 0))
                    if reachedNPC then
                        CommF:InvokeServer("StartQuest", currentData.Quest, currentData.QuestLvl)
                        task.wait(0.2)
                    end
                else
                    local target = GetClosestTarget(currentData.Mob)
                    if target and target:FindFirstChild("HumanoidRootPart") then
                        CancelTween()
                        if Settings.AutoEquip then EquipWeapon() end
                        local mobCFrame = target.HumanoidRootPart.CFrame
                        local safeCFrame = mobCFrame * CFrame.new(0, Settings.HeightOffset, Settings.BackOffset)
                        hrp.CFrame = CFrame.lookAt(safeCFrame.Position, target.HumanoidRootPart.Position)
                        hrp.AssemblyLinearVelocity = Vector3.new(0, 0, 0)
                    else
                        SafeTravel(currentData.MobCFrame * CFrame.new(0, 20, 0))
                    end
                end
            end
        end
    end
end)
