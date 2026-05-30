// ========== 题材卡片（用于灵感提示） ==========
export interface GenreCardData {
  id: string
  emoji: string
  name: string
  desc: string
  tags: string[]
  gender: 'male' | 'female' | 'both'  // 男频/女频/通用
}

export const GENRE_CARDS: GenreCardData[] = [
  // 男频
  {
    id: 'xuanhuan',
    emoji: '⚔️',
    name: '玄幻修仙',
    desc: '修炼升级，纵横天下，逆天改命',
    tags: ['升级', '打怪', '法宝', '境界突破'],
    gender: 'male',
  },
  {
    id: 'urban_power',
    emoji: '🏙️',
    name: '都市异能',
    desc: '隐藏身份，超能力觉醒，都市称霸',
    tags: ['异能', '隐藏身份', '打脸', '逆袭'],
    gender: 'male',
  },
  {
    id: 'history_build',
    emoji: '👑',
    name: '历史架空',
    desc: '朝堂权谋，战争策略，文明建设',
    tags: ['权谋', '争霸', '建设', '帝王'],
    gender: 'male',
  },
  {
    id: 'scifi_star',
    emoji: '🚀',
    name: '科幻星际',
    desc: '星际战争，科技发展，文明探索',
    tags: ['星际', '机甲', '科技', '探索'],
    gender: 'male',
  },
  {
    id: 'game_system',
    emoji: '🎮',
    name: '游戏系统',
    desc: '带着系统穿越，任务升级两不误',
    tags: ['系统', '升级', '任务', '数据化'],
    gender: 'male',
  },
  {
    id: 'basebuilding',
    emoji: '🏗️',
    name: '种田基建',
    desc: '从零开始建设势力，用知识改变世界',
    tags: ['种田', '基建', '工业', '经营'],
    gender: 'male',
  },
  // 女频
  {
    id: 'sweet_love',
    emoji: '💕',
    name: '甜宠恋爱',
    desc: '高甜互动，撒糖日常，宠溺无度',
    tags: ['甜宠', '撒糖', '日常', '双向奔赴'],
    gender: 'female',
  },
  {
    id: 'palace_fight',
    emoji: '🏮',
    name: '宫斗宅斗',
    desc: '后宫争宠，家族内斗，步步为营',
    tags: ['宫斗', '宅斗', '权谋', '逆袭'],
    gender: 'female',
  },
  {
    id: 'rebirth_revenge',
    emoji: '🔄',
    name: '重生复仇',
    desc: '重回过去，改写命运，手撕渣人',
    tags: ['重生', '复仇', '打脸', '逆袭'],
    gender: 'female',
  },
  {
    id: 'ancient_love',
    emoji: '✨',
    name: '古言情缘',
    desc: '古代背景的爱恨情仇，虐恋情深',
    tags: ['古言', '虐恋', '宫闱', '江湖'],
    gender: 'female',
  },
  {
    id: 'transmigration',
    emoji: '📖',
    name: '穿书穿越',
    desc: '穿越到书中世界，先知先觉改写命运',
    tags: ['穿书', '穿越', '先知', '改命'],
    gender: 'female',
  },
  {
    id: 'modern_love',
    emoji: '💼',
    name: '现代言情',
    desc: '都市甜蜜互动，职场爱情，双向成长',
    tags: ['现言', '职场', '都市', '甜宠'],
    gender: 'female',
  },
  // 通用
  {
    id: 'mystery',
    emoji: '🔍',
    name: '悬疑推理',
    desc: '抽丝剥茧，真相只有一个',
    tags: ['推理', '破案', '悬疑', '反转'],
    gender: 'both',
  },
  {
    id: 'apocalypse',
    emoji: '☢️',
    name: '末世生存',
    desc: '末日降临，生存挑战，基地建设',
    tags: ['末世', '生存', '基地', '变异'],
    gender: 'both',
  },
  {
    id: 'esports',
    emoji: '🏆',
    name: '竞技体育',
    desc: '电竞/体育赛场，热血拼搏，冠军之路',
    tags: ['电竞', '体育', '竞技', '热血'],
    gender: 'both',
  },
]

// ========== 平台场景卡片（业务约束） ==========
export interface PlatformCardData {
  id: string
  emoji: string
  name: string
  desc: string
  platform: string
  lengthType: string
  targetWords: number
  targetChapters: number
  chapterWordRange: [number, number]
  updateFrequency: string
  style: string
}

export const PLATFORM_CARDS: PlatformCardData[] = [
  {
    id: 'short',
    emoji: '📱',
    name: '小红书爆款',
    desc: '短篇高能，开头即高潮，适合引流种草',
    platform: '小红书',
    lengthType: 'short',
    targetWords: 30000,
    targetChapters: 10,
    chapterWordRange: [2000, 4000],
    updateFrequency: '完结后发布',
    style: '极度压缩，情绪拉满，500字内抓住读者',
  },
  {
    id: 'fanqie_standard',
    emoji: '🍅',
    name: '番茄日更',
    desc: '每天 3000-4000 字，前3章见爽点，算法推荐',
    platform: '番茄小说',
    lengthType: 'medium',
    targetWords: 120000,
    targetChapters: 40,
    chapterWordRange: [2500, 3500],
    updateFrequency: '日更 3000+',
    style: '节奏极快，每章有钩子，不能慢热',
  },
  {
    id: 'fanqie_long',
    emoji: '📚',
    name: '番茄长篇',
    desc: '日更 5000 字，长尾效应，广告分成',
    platform: '番茄小说',
    lengthType: 'long',
    targetWords: 300000,
    targetChapters: 100,
    chapterWordRange: [3000, 5000],
    updateFrequency: '日更 5000+',
    style: '稳定更新，每卷有高潮，持续吸引读者',
  },
  {
    id: 'qidian',
    emoji: '📕',
    name: '起点精品',
    desc: '付费订阅，世界观宏大，核心男频阵地',
    platform: '起点中文网',
    lengthType: 'long',
    targetWords: 300000,
    targetChapters: 100,
    chapterWordRange: [3000, 5000],
    updateFrequency: '日更 4000+',
    style: '允许铺垫（前3万字见真章），世界观构建重要',
  },
  {
    id: 'jjwxc',
    emoji: '🌸',
    name: '晋江精品',
    desc: '女频精品，注重文笔和情感铺垫',
    platform: '晋江文学城',
    lengthType: 'medium',
    targetWords: 80000,
    targetChapters: 30,
    chapterWordRange: [3000, 6000],
    updateFrequency: '日更/隔日更',
    style: '注重文笔，允许慢热但需有吸引力，完结后有长尾',
  },
]

// ========== 主角性格模板 ==========
export interface CharacterTemplate {
  id: string
  name: string
  desc: string
  suitableGenres: string[]
  example: string
  gender: 'male' | 'female'
}

export const PROTAGONIST_TEMPLATES: CharacterTemplate[] = [
  // 男频
  { id: 'endure', name: '隐忍型', desc: '低调蛰伏，一朝爆发，惊艳所有人', suitableGenres: ['逆袭打脸', '都市', '玄幻'], example: '萧炎（斗破苍穹）', gender: 'male' },
  { id: 'domineer', name: '霸气型', desc: '天生王者气质，以力服人，唯我独尊', suitableGenres: ['玄幻', '仙侠', '争霸'], example: '石昊（完美世界）', gender: 'male' },
  { id: 'schemer', name: '腹黑型', desc: '笑里藏刀，算无遗策，智商碾压', suitableGenres: ['权谋', '都市', '架空历史'], example: '陈平安（剑来）', gender: 'male' },
  { id: 'sharp_tongue', name: '毒舌型', desc: '嘴炮无敌，怼天怼地，但内心有底线', suitableGenres: ['都市', '轻喜剧', '系统文'], example: '徐凤年（雪中悍刀行）', gender: 'male' },
  { id: 'funny', name: '逗逼型', desc: '插科打诨，搞笑担当，但关键时刻靠得住', suitableGenres: ['轻松向', '日常', '冒险'], example: '张楚岚（一人之下）', gender: 'male' },
  { id: 'cold', name: '高冷型', desc: '沉默寡言，实力深不可测，自带气场', suitableGenres: ['仙侠', '高武', '星际'], example: '叶凡（遮天）', gender: 'male' },
  { id: 'rogue', name: '痞帅型', desc: '玩世不恭，亦正亦邪，魅力十足', suitableGenres: ['都市', '江湖', '谍战'], example: '秦羽（星辰变）', gender: 'male' },
  { id: 'hot_blood', name: '热血型', desc: '满腔热血，重情重义，永不言弃', suitableGenres: ['热血战斗', '竞技', '冒险'], example: '路飞（借鉴日漫）', gender: 'male' },
  { id: 'buddha', name: '佛系型', desc: '随遇而安，但被逼无奈只能出手', suitableGenres: ['日常', '轻松', '种田'], example: '许七安（大奉打更人）', gender: 'male' },
  { id: 'mastermind', name: '老阴比', desc: '深谋远虑，布局千里，一切尽在掌握', suitableGenres: ['权谋', '官场', '谍战'], example: '范闲（庆余年）', gender: 'male' },
  // 女频
  { id: 'tough_girl', name: '坚韧型', desc: '历经磨难不屈服，越挫越勇终逆袭', suitableGenres: ['虐恋', '年代', '宫斗'], example: '花千骨', gender: 'female' },
  { id: 'sweet_girl', name: '甜美型', desc: '天真可爱，人见人爱，自带桃花体质', suitableGenres: ['甜宠', '校园', '穿书'], example: '薛杉杉（杉杉来了）', gender: 'female' },
  { id: 'smart_girl', name: '聪慧型', desc: '才智过人，以智取胜，不靠男人', suitableGenres: ['宫斗', '经商', '权谋'], example: '甄嬛（甄嬛传）', gender: 'female' },
  { id: 'cool_girl', name: '飒爽型', desc: '雷厉风行，英姿飒爽，大女主气场', suitableGenres: ['事业文', '独立成长', '现代'], example: '盛明兰（知否）', gender: 'female' },
  { id: 'schemer_girl', name: '腹黑型', desc: '外表无害内心城府深，扮猪吃老虎', suitableGenres: ['宫斗', '宅斗', '重生'], example: '魏璎珞（延禧攻略）', gender: 'female' },
  { id: 'gentle_girl', name: '温柔型', desc: '善良体贴，以柔克刚，润物细无声', suitableGenres: ['甜宠', '都市', '古言'], example: '薛宝钗型', gender: 'female' },
  { id: 'tsundere', name: '傲娇型', desc: '嘴上嫌弃实际在意，反差萌', suitableGenres: ['都市', '校园', '轻喜剧'], example: '日系ACG经典', gender: 'female' },
  { id: 'queen', name: '女王型', desc: '霸道总裁/女帝，掌控一切', suitableGenres: ['女尊', '现代霸总', '重生'], example: '女强人设', gender: 'female' },
]

// ========== 感情线模式（男频适用） ==========
export interface RomanceMode {
  id: string
  name: string
  desc: string
  safety: number  // 1-5，5 最安全
  suitableGenres: string[]
}

export const ROMANCE_MODES: RomanceMode[] = [
  { id: 'none', name: '无女主', desc: '纯事业线，无感情戏或极少', safety: 5, suitableGenres: ['升级流', '争霸', '探险'] },
  { id: 'single', name: '单女主', desc: '一对一专一感情线，女主戏份重要', safety: 5, suitableGenres: ['都市', '仙侠', '玄幻'] },
  { id: 'harem', name: '后宫', desc: '多女主，每位有独立人设和故事线', safety: 3, suitableGenres: ['玄幻', '都市', '架空历史'] },
  { id: 'ambiguous', name: '暧昧', desc: '有感情戏但不确定关系，若即若离', safety: 3, suitableGenres: ['都市', '校园', '轻小说'] },
  { id: 'confidante', name: '红颜知己', desc: '不谈恋爱，但有深度情感羁绊', safety: 4, suitableGenres: ['武侠', '仙侠', '权谋'] },
  { id: 'contract_love', name: '先婚后爱', desc: '先结婚/契约关系，后产生真感情', safety: 4, suitableGenres: ['都市', '古言', '豪门'] },
]

// ========== 女主性格模板（有女主/后宫时使用） ==========
export interface HeroineTemplate {
  id: string
  name: string
  desc: string
  suitableScenes: string[]
}

export const HEROINE_TEMPLATES: HeroineTemplate[] = [
  { id: 'ice_beauty', name: '冰山美人', desc: '外冷内热，只对男主破功', suitableScenes: ['仙侠', '玄幻', '都市'] },
  { id: 'lively', name: '天真活泼', desc: '开朗乐观，是男主的开心果', suitableScenes: ['校园', '轻松向', '甜宠'] },
  { id: 'gentle', name: '温柔贤惠', desc: '默默守护，无条件支持男主', suitableScenes: ['都市', '年代', '种田'] },
  { id: 'strong_woman', name: '女强人', desc: '独立自主，与男主势均力敌', suitableScenes: ['都市', '商战', '星际'] },
  { id: 'schemer_h', name: '腹黑绿茶', desc: '表面柔弱实则心机深，亦正亦邪', suitableScenes: ['宫斗', '宅斗', '权谋'] },
  { id: 'childhood', name: '青梅竹马', desc: '从小一起长大，感情基础深厚', suitableScenes: ['校园', '都市', '仙侠'] },
  { id: 'tsundere_h', name: '傲娇大小姐', desc: '嘴上嫌弃实际在意，反差萌', suitableScenes: ['都市', '校园', '轻喜剧'] },
  { id: 'foodie', name: '呆萌吃货', desc: '天然呆+吃货属性，无攻击性', suitableScenes: ['轻松向', '日常', '甜宠'] },
  { id: 'mature', name: '御姐型', desc: '成熟性感，比男主年长或心理成熟', suitableScenes: ['都市', '职场', '现代'] },
  { id: 'swordwoman', name: '侠女型', desc: '行侠仗义，英姿飒爽，巾帼不让须眉', suitableScenes: ['武侠', '仙侠', '江湖'] },
]

// ========== 输入提示 ==========
export const STEP_HINTS = {
  gender: {
    title: '你的小说写给谁看？',
    subtitle: '这决定了后续所有选项的方向',
  },

  genre: {
    title: '你想写什么类型的故事？',
    subtitle: '点击卡片选择题材，或者手动输入',
    placeholder: '如：赛博朋克、克苏鲁、美食...',
  },

  conflict: {
    title: '你的主角是谁？遇到了什么事？',
    subtitle: '从这几个角度想一想，写下来就行',
    angles: [
      { icon: '👤', label: '主角是谁？', hint: '身份、职业、性格特点' },
      { icon: '💥', label: '发生了什么？', hint: '导致主角处境改变的关键事件' },
      { icon: '🎯', label: '主角想做什么？', hint: '目标、动机、想改变什么' },
      { icon: '🚧', label: '什么在阻碍他？', hint: '对手、环境、自身缺陷' },
    ],
    placeholder: '例如：一个材料学博士，研究成果被学长背叛，加上长期熬夜猝死，穿越到魔法世界的落魄男爵家。他决定用现代工业知识改造这个快要衰落的魔法世界...',
  },

  platform: {
    title: '你打算发到哪个平台？',
    subtitle: '选择发布场景，我们会帮你规划篇幅',
    customHint: '也可以自己设定字数和章节数',
  },

  character: {
    title: '说说你的主角',
    subtitle: '选择性格模板，或者自由描述',
  },

  romance: {
    title: '感情线怎么安排？',
    subtitle: '选择感情线模式',
  },

  heroine: {
    title: '女主是什么性格？',
    subtitle: '选择女主性格模板，或者自由描述',
  },

  style: {
    title: '你喜欢什么风格？',
    subtitle: '可以写参考作品、风格偏好，或者直接描述你想要的感觉',
    placeholder: '例如：诙谐幽默，像《庆余年》那种穿越+吐槽的感觉，爽文但不无脑，主角靠真本事碾压...',
  },
}
