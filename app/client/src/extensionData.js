export const EXTENSION_POINTS = [
  {
    id: "nutrition-meal-template",
    title: "减脂餐模板库",
    owner: "注册营养师 / 健康管理师",
    problem: "用户知道要少油少糖，但很难把鸡蛋、鱼肉、瘦肉、米饭、土豆、豆腐等常见食材组合成稳定可执行的一日餐。",
    feature: "提供按早午晚餐分类的高蛋白、控油、控主食模板，直接给出食材组合、营养侧重点和执行提示。",
    acceptance: "页面能展示不少于 6 个餐食模板；用户可快速识别餐次、核心食材、宏量营养重点和可执行建议。"
  },
  {
    id: "nutrition-shopping-plan",
    title: "补充采购清单",
    owner: "营养顾问 / 家庭备餐负责人",
    problem: "用户已有常见食材，但采购时容易缺少优质蛋白、低热量蔬菜和可控零食，导致临时外卖或高热量加餐。",
    feature: "按蛋白质、蔬菜、主食和控零食分组提供补充采购建议，便于周计划备餐和冰箱管理。",
    acceptance: "采购建议必须分组清晰，覆盖 protein、vegetable、carb、snackControl 四类，并能直接渲染为列表。"
  },
  {
    id: "nutrition-portion-guide",
    title: "份量与餐盘比例提示",
    owner: "营养师 / 运动减脂教练",
    problem: "用户常见误区不是食材选择错误，而是米饭、土豆、油脂和肉类份量不稳定，导致热量缺口难以维持。",
    feature: "在模板文案中强调蛋白优先、蔬菜占半盘、主食按训练量微调、烹调少油的原则。",
    acceptance: "每个餐食模板都应有 macroFocus 和 tip 字段，能向用户解释为什么这样搭配以及如何控制份量。"
  },
  {
    id: "nutrition-behavior-support",
    title: "控饿与复食行为支持",
    owner: "健康管理师 / 行为营养教练",
    problem: "减脂期失败常发生在下午加餐、晚餐过饿、夜间零食和高油重口味复食环节。",
    feature: "通过牛奶、豆腐、鸡蛋、鱼肉、青菜等高饱腹食材，以及可控零食建议，降低饥饿感和冲动进食。",
    acceptance: "数据文案要避免极端节食表达，强调饱腹感、可持续、低油烹调和稳定执行。"
  }
];

export const MEAL_TEMPLATES = [
  {
    title: "鸡蛋牛奶小米粥早餐",
    mealType: "breakfast",
    ingredients: ["鸡蛋", "牛奶", "小米粥", "青菜"],
    macroFocus: "高饱腹蛋白 + 温和碳水 + 少量蔬菜纤维",
    tip: "小米粥控制在一小碗，鸡蛋优先水煮或蒸蛋，牛奶选择纯牛奶或低脂奶，避免额外加糖。"
  },
  {
    title: "清蒸鱼肉青菜米饭午餐",
    mealType: "lunch",
    ingredients: ["鱼肉", "米饭", "青菜", "辣椒"],
    macroFocus: "优质蛋白 + 适量主食 + 高纤维蔬菜",
    tip: "鱼肉清蒸或少油煎，米饭按半拳到一拳调整，辣椒用于提味，不用重油辣酱。"
  },
  {
    title: "瘦肉炒茄子配米饭",
    mealType: "lunch",
    ingredients: ["瘦肉", "茄子", "米饭", "青菜"],
    macroFocus: "瘦肉蛋白 + 控油蔬菜 + 稳定碳水",
    tip: "茄子先蒸后炒或用少油焖，瘦肉切片快炒，米饭减量并增加青菜，避免茄子吸油过多。"
  },
  {
    title: "豆腐青菜土豆晚餐",
    mealType: "dinner",
    ingredients: ["豆腐", "青菜", "土豆", "辣椒"],
    macroFocus: "植物蛋白 + 高纤维蔬菜 + 低脂饱腹主食",
    tip: "土豆蒸煮后替代部分米饭，豆腐少油煎或炖汤，晚餐保持清淡，适合不训练日。"
  },
  {
    title: "鸡蛋豆腐青菜汤",
    mealType: "dinner",
    ingredients: ["鸡蛋", "豆腐", "青菜"],
    macroFocus: "双来源蛋白 + 低热量高体积",
    tip: "用汤类增加饱腹感，少盐少油，若当天运动量较大可额外加半小碗米饭或少量土豆。"
  },
  {
    title: "瘦肉辣椒土豆便当",
    mealType: "lunch",
    ingredients: ["瘦肉", "辣椒", "土豆", "青菜"],
    macroFocus: "高蛋白 + 可控淀粉 + 微辣提升满足感",
    tip: "土豆作为主食来源时不再叠加大量米饭，瘦肉用里脊或后腿肉，辣椒少油快炒。"
  },
  {
    title: "鱼肉豆腐青菜晚餐",
    mealType: "dinner",
    ingredients: ["鱼肉", "豆腐", "青菜"],
    macroFocus: "高蛋白低脂 + 高饱腹 + 低碳水",
    tip: "适合晚餐想减轻负担时使用，鱼肉和豆腐不要同时重油煎，优先炖、蒸、煮。"
  }
];

export const SHOPPING_LIST = {
  protein: [
    "鸡胸肉或去皮鸡腿肉",
    "低脂纯牛奶",
    "无糖酸奶",
    "虾仁",
    "低脂豆制品",
    "瘦牛肉或猪里脊"
  ],
  vegetable: [
    "西兰花",
    "生菜",
    "黄瓜",
    "番茄",
    "菌菇",
    "菠菜或油麦菜"
  ],
  carb: [
    "燕麦",
    "红薯",
    "玉米",
    "糙米",
    "全麦面包",
    "荞麦面"
  ],
  snackControl: [
    "无糖豆浆",
    "原味坚果小包装",
    "低糖水果",
    "海苔",
    "无糖茶饮",
    "高可可黑巧小份装"
  ]
};
