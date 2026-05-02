// script.js
const COLORS = {
    bg: '#0D1B2E',
    panelBg: '#1E293B',
    textMain: '#F1F5F9',
    textDim: '#d0d8e3',
    accent: '#FBBF24',
    red: '#E24B4A',
    muted: '#828c9b',
    blue: '#378ADD'
};

const REGION_COLORS = {
    'Asia'     : '#ad7efd',
    'Europe'   : '#50f3ff',
    'Americas' : '#31f8b9',
    'Africa'   : '#FB923C',
    'Oceania'  : '#BE185D',
    'Others'   : '#475569',
};

const PILLARS = [
    {key: 'ai_talent',              label: 'Talent',      color: '#7C5CFF', icon: 'talent'},
    {key: 'ai_infrastructure',      label: 'Infrastructure', color: '#7DD3FC', icon: 'infra'},
    {key: 'ai_government_strategy', label: 'Gov. Strategy',  color: '#FBBF24', icon: 'strategy'},
    {key: 'ai_research',            label: 'Research',    color: '#22D3EE', icon: 'research'},
    {key: 'ai_development',         label: 'Development', color: '#34D399', icon: 'development'},
    {key: 'ai_commercial',          label: 'Commercial',  color: '#CBD5E1', icon: 'commercial'},
];

const REGION_MAP = {
    'United States':'Americas','Canada':'Americas','Mexico':'Americas',
    'Brazil':'Americas','Colombia':'Americas','Argentina':'Americas',
    'China':'Asia','Japan':'Asia','South Korea':'Asia','India':'Asia',
    'Singapore':'Asia','Malaysia':'Asia','Thailand':'Asia','Indonesia':'Asia',
    'Vietnam':'Asia','Philippines':'Asia','Taiwan':'Asia','Israel':'Asia',
    'United Kingdom':'Europe','Germany':'Europe','France':'Europe',
    'Finland':'Europe','Sweden':'Europe','Netherlands':'Europe',
    'Spain':'Europe','Italy':'Europe','Poland':'Europe','Denmark':'Europe',
    'Norway':'Europe','Switzerland':'Europe',
    'Nigeria':'Africa','Egypt':'Africa','Morocco':'Africa','South Africa':'Africa',
    'Australia':'Oceania','New Zealand':'Oceania',
};

function getCountryColor(country, region) {
    if (country === 'Indonesia') return COLORS.red;
    return REGION_COLORS[region] || COLORS.muted;
}

function getPillarIcon(type) {
    const icons = {
        talent:      '<svg viewBox="0 0 24 24"><path d="M8 19v-2a4 4 0 0 1 8 0v2"/><circle cx="12" cy="8" r="4"/><path d="M4 21h16"/></svg>',
        infra:       '<svg viewBox="0 0 24 24"><rect x="5" y="4" width="14" height="6" rx="2"/><rect x="5" y="14" width="14" height="6" rx="2"/><path d="M8 7h.01M8 17h.01M12 10v4"/></svg>',
        strategy:    '<svg viewBox="0 0 24 24"><circle cx="12" cy="12" r="8"/><path d="M12 7v5l4 2"/><path d="M4 20l3-3M20 4l-3 3"/></svg>',
        research:    '<svg viewBox="0 0 24 24"><path d="M10 4v6l-5 8a2 2 0 0 0 2 3h10a2 2 0 0 0 2-3l-5-8V4"/><path d="M8 4h8M8 15h8"/></svg>',
        development: '<svg viewBox="0 0 24 24"><path d="M8 17l-5-5 5-5M16 7l5 5-5 5"/><path d="M14 4l-4 16"/></svg>',
        commercial:  '<svg viewBox="0 0 24 24"><path d="M5 8h14l-1 12H6z"/><path d="M9 8a3 3 0 0 1 6 0"/><path d="M8 13h8"/></svg>',
    };
    return icons[type] || icons.strategy;
}

function drawInsightOval(g, x, y, lines, options = {}) {
    const rx = options.rx || 115;
    const ry = options.ry || 38;
    const textColor = options.textColor || '#6F7F94';
    const strokeColor = options.strokeColor || '#2B3A4E';
    const fontSize = options.fontSize || 12;

    const group = g.append("g").attr("class", "insight-oval");
    group.append("ellipse")
        .attr("cx", x).attr("cy", y)
        .attr("rx", rx).attr("ry", ry)
        .attr("fill", "transparent")
        .attr("stroke", strokeColor)
        .attr("stroke-width", 1.4)
        .attr("stroke-dasharray", "5 6")
        .attr("stroke-opacity", 0.78);

    lines.forEach((line, i) => {
        const offset = (i - (lines.length - 1) / 2) * fontSize * 1.25;
        group.append("text")
            .attr("x", x).attr("y", y + offset)
            .attr("fill", textColor)
            .attr("font-size", `${fontSize}px`)
            .attr("font-weight", 700)
            .attr("text-anchor", "middle")
            .attr("alignment-baseline", "middle")
            .text(line);
    });
}

function keepBubbleInsideColumn(y, r, topLimit, bottomLimit) {
    return Math.max(topLimit + r, Math.min(bottomLimit - r, y));
}

// ─────────────────────────────────────────────
Promise.all([
    d3.csv("ai_data.csv"),
    d3.csv("fitped_raw.csv")
]).then(([aiData, fpData]) => {

    aiData.forEach(d => {
        let cleanRow = {};
        for (let k in d) {
            let cln = k.trim().toLowerCase().replace(/ /g, '_');
            cleanRow[cln] = d[k];
        }
        Object.assign(d, cleanRow);

        d.ai_overall_score      = +d.ai_overall_score;
        d.gdp_per_capita        = +d.gdp_per_capita;
        if (isNaN(d.gdp_per_capita) || d.gdp_per_capita === 0) {
            if (d.country === 'South Korea') d.gdp_per_capita = 32000;
            else if (d.country === 'Egypt')  d.gdp_per_capita = 3000;
            else                             d.gdp_per_capita = 5000;
        }
        d.ai_government_strategy = +d.ai_government_strategy;
        d.internet_usage_pct     = +d.internet_usage_pct;
        d.region = REGION_MAP[d.country] || 'Others';
        PILLARS.forEach(p => { d[p.key] = +d[p.key] || 0; });
    });

    renderSection2(aiData);
    renderSection3(aiData);
    renderSection4(fpData);
});

// ─────────────────────────────────────────────
// SECTION 2 — Sankey + Bar + Bubble
// ─────────────────────────────────────────────
function renderSection2(data) {
    let sortedGlobal = [...data].sort((a, b) => b.ai_overall_score - a.ai_overall_score);
    let top12    = sortedGlobal.slice(0, 12).map(d => d.country);
    let asean    = ['Malaysia','Thailand','Indonesia','Vietnam','Philippines'];
    let peers    = ['Brazil','India','Colombia','Egypt','Morocco','Nigeria','Mexico'];

    let selectedNames = new Set([...top12, ...asean, ...peers]);
    let df = data.filter(d => selectedNames.has(d.country));
    df.sort((a, b) => b.gdp_per_capita - a.gdp_per_capita);

    const N = df.length;
    const TOTAL_GDP = d3.sum(df, d => d.gdp_per_capita);

    const container = document.getElementById("flow-charts");
    const width  = container.clientWidth;
    const height = container.clientHeight;
    const svg = d3.select("#flow-charts").append("svg").attr("width", width).attr("height", height);

    const sankeyW = width * 0.52;
    const barW    = width * 0.33;
    const bubW    = width * 0.15;
    const REGION_GAP = 50;

    const REGION_ORDER = ['Americas','Europe','Asia','Oceania','Others','Africa'];
    let uniqueRegions = [...new Set(df.map(d => d.region))];
    let regionsInOrder = uniqueRegions.sort((a, b) =>
        REGION_ORDER.indexOf(a) - REGION_ORDER.indexOf(b));
    let gapBudget  = regionsInOrder.length * REGION_GAP;
    let bandBudget = height - gapBudget - 40;

    df.forEach(d => { d.h = Math.max(9, (d.gdp_per_capita / TOTAL_GDP) * bandBudget); });

    let actualBandTotal = d3.sum(df, d => d.h);
    let curY = height - 20;
    regionsInOrder.slice().reverse().forEach(reg => {
        let regRows = df.filter(d => d.region === reg).reverse();
        regRows.forEach(d => {
            d.left_yb = curY;
            d.left_yt = curY - d.h;
            d.left_yc = curY - d.h / 2;
            curY -= d.h;
        });
        curY -= REGION_GAP;
    });

    let rightGap   = (height - 40 - actualBandTotal) / (N - 1);
    let rightCurY  = height - 20;
    df.slice().reverse().forEach(d => {
        d.right_yb = rightCurY;
        d.right_yt = rightCurY - d.h;
        d.right_yc = rightCurY - d.h / 2;
        rightCurY -= (d.h + rightGap);
    });

    const sankeyLeftMargin = 160;
    const sankeyG = svg.append("g").attr("transform", `translate(${sankeyLeftMargin},0)`);
    const sankeyInnerW = sankeyW - sankeyLeftMargin;

    // Region labels
    regionsInOrder.forEach(reg => {
        let regRows = df.filter(d => d.region === reg);
        let topY = d3.min(regRows, d => d.left_yt);
        let botY = d3.max(regRows, d => d.left_yb);
        let midY = (topY + botY) / 2;
        let rc   = REGION_COLORS[reg] || COLORS.muted;

        sankeyG.append("line")
            .attr("x1", -30).attr("x2", -30).attr("y1", botY).attr("y2", topY)
            .attr("stroke", rc).attr("stroke-width", 4).attr("stroke-linecap", "round");

        sankeyG.append("text")
            .attr("x", -40).attr("y", midY)
            .attr("fill", rc).attr("font-size", "13px").attr("font-weight", "800")
            .attr("text-anchor", "end").attr("alignment-baseline", "middle")
            .style("letter-spacing", "2px").text(reg.toUpperCase());
    });

    df.forEach((d) => {
        let xl = 0, xr = sankeyInnerW;
        let isIndo = d.country === 'Indonesia';
        const col  = getCountryColor(d.country, d.region);

        let pathData = `M ${xl} ${d.left_yb}
            C ${xl + (xr-xl)*0.4} ${d.left_yb}, ${xl + (xr-xl)*0.6} ${d.right_yb}, ${xr} ${d.right_yb}
            L ${xr} ${d.right_yt}
            C ${xl + (xr-xl)*0.6} ${d.right_yt}, ${xl + (xr-xl)*0.4} ${d.left_yt}, ${xl} ${d.left_yt} Z`;

        sankeyG.append("path")
            .attr("d", pathData)
            .attr("fill", col)
            .attr("opacity", isIndo ? 1.0 : 0.6)
            .attr("class", "sankey-link")
            .style("cursor", "default");

        if (d.h > 15) {
            sankeyG.append("text")
                .attr("x", xl + 5).attr("y", d.left_yc)
                .attr("fill", isIndo ? "#FFFFFF" : "#d1d3d4")
                .attr("font-size", "9px").attr("font-weight", isIndo ? "700" : "400")
                .attr("text-anchor", "start").attr("alignment-baseline", "middle")
                .style("pointer-events", "none")
                .text(`$${(d.gdp_per_capita / 1000).toFixed(1)}k`);
        }

        sankeyG.append("text")
            .attr("x", xr - 15).attr("y", d.right_yc)
            .attr("fill", isIndo ? "#FFFFFF" : COLORS.textMain)
            .attr("font-size", isIndo ? "10px" : "9px")
            .attr("font-weight", isIndo ? "600" : "200")
            .attr("text-anchor", "end").attr("alignment-baseline", "middle")
            .style("pointer-events", "none").text(d.country);
    });

    // Bar chart
    const barG = svg.append("g")
        .attr("transform", `translate(${sankeyLeftMargin + sankeyInnerW}, 0)`);
    const xScaleBar = d3.scaleLinear().domain([0, 100]).range([0, barW - 10]);

    df.forEach(d => {
        const col   = getCountryColor(d.country, d.region);
        let isIndo  = d.country === 'Indonesia';

        barG.append("rect")
            .attr("x", 0).attr("y", d.right_yt)
            .attr("width", xScaleBar(d.ai_government_strategy))
            .attr("height", d.h)
            .attr("fill", col)
            .attr("opacity", isIndo ? 1.0 : 0.7);

        barG.append("text")
            .attr("x", xScaleBar(d.ai_government_strategy) + 8).attr("y", d.right_yc)
            .attr("fill", isIndo ? COLORS.red : col)
            .attr("font-size", "10px").attr("font-weight", isIndo ? "bold" : "normal")
            .attr("alignment-baseline", "middle")
            .text(Math.round(d.ai_government_strategy));
    });

    // Bubbles
    const bubG = svg.append("g")
        .attr("transform", `translate(${sankeyLeftMargin + sankeyInnerW + (barW - 10) + 40}, 0)`);
    const radScale = d3.scaleSqrt()
        .domain([0, d3.max(df, d => d.ai_overall_score)])
        .range([7, 32]);

    const bubbleNodes = df.map(d => ({
        data: d,
        r: radScale(d.ai_overall_score),
        y: keepBubbleInsideColumn(d.right_yc, radScale(d.ai_overall_score), 12, height - 12)
    }));

    bubbleNodes.forEach(node => {
        const d   = node.data;
        const col = getCountryColor(d.country, d.region);
        let isIndo = d.country === 'Indonesia';

        bubG.append("circle")
            .attr("cx", bubW / 2).attr("cy", node.y).attr("r", node.r)
            .attr("fill", col)
            .attr("fill-opacity", isIndo ? 0.72 : 0.32)
            .attr("stroke", col)
            .attr("stroke-width", isIndo ? 2.2 : 1.2);
    });

    const indo = df.find(d => d.country === "Indonesia");
    if (indo) {
        drawInsightOval(svg,
            sankeyLeftMargin + sankeyInnerW + barW * 0.76, indo.right_yc,
            ["Strategi nasional", "masih tertinggal"],
            { rx: 120, ry: 34, fontSize: 15,
              textColor:   '#378ADD',
              strokeColor: '#378ADD'    
            });
    }
}

// ─────────────────────────────────────────────
// SECTION 3 — Stacked Bar (Pillars)
// FIX 1: compute SVG height from row count, not container.clientHeight
// FIX 2: wider left margin so "United Kingdom" never clips
// ─────────────────────────────────────────────
function renderSection3(data) {
    const SUBSET_NAMES = [
        'United States','China','Singapore','United Kingdom','Germany',
        'Finland','India','Brazil','Malaysia','Vietnam','Indonesia',
        'Colombia','Nigeria'
    ];

    let ds3 = SUBSET_NAMES
        .map(c => data.find(d => d.country === c))
        .filter(Boolean);

    // Legend
    const legendContainer = d3.select("#pillar-legend");
    PILLARS.forEach(p => {
        let item = legendContainer.append("div").attr("class", "legend-item");
        item.append("div")
            .attr("class", "legend-icon")
            .style("color", p.color)
            .html(getPillarIcon(p.icon));
        item.append("div").text(p.label);
    });

    // ── FIX 1: derive height from row count ──────────────────────────
    const ROW_HEIGHT  = 32;   // px per country row
    const ROW_PADDING = 0.35; // band padding fraction (same as scaleBand)
    const margin = { top: 20, right: 30, bottom: 20, left: 140 }; // ← FIX 2: left 140
    

    const innerH = ds3.length * ROW_HEIGHT / (1 - ROW_PADDING);
    const height = innerH + margin.top + margin.bottom;

    const container = document.getElementById("pillars-chart");
    const width     = container.clientWidth || 1400;
    const innerW    = width - margin.left - margin.right;
    // ────────────────────────────────────────────────────────────────

    const svg = d3.select("#pillars-chart")
        .append("svg")
        .attr("width", width)
        .attr("height", height);         // ← explicit, computed height

    const y = d3.scaleBand()
        .domain(ds3.map(d => d.country))
        .range([0, innerH])
        .padding(ROW_PADDING);

    const x = d3.scaleLinear()
        .domain([0, 600])
        .range([0, innerW]);

    const g = svg.append("g")
        .attr("transform", `translate(${margin.left},${margin.top})`);

    ds3.forEach(d => {
        let currentX = 0;
        let isIndo   = d.country === 'Indonesia';

        PILLARS.forEach(p => {
            let val = d[p.key] || 0;

            // Gov. Strategy bar gets a red outline for Indonesia to make it pop
            if (isIndo && p.key === 'ai_government_strategy') {
                g.append("rect")
                    .attr("x", x(currentX) - 1).attr("y", y(d.country) - 2)
                    .attr("width", x(val) + 2)
                    .attr("height", y.bandwidth() + 4)
                    .attr("fill", "none")
                    .attr("stroke", "#E8193C")
                    .attr("stroke-width", 2)
                    .attr("rx", 2)
                    .attr("opacity", 0.85);
            }

            g.append("rect")
                .attr("x", x(currentX)).attr("y", y(d.country))
                .attr("width", x(val)).attr("height", y.bandwidth())
                .attr("fill", p.color)
                .attr("opacity", 0.88);

            currentX += val;
        });

        // Oval annotation for Indonesia
        if (isIndo) {
            let ovalX = Math.min(x(currentX) + 108, innerW - 110);
            drawInsightOval(g, ovalX, y(d.country) + y.bandwidth() / 2,
                ["Gov. Strategy", "19/100"],
                {   rx: 80, ry: 22, fontSize: 13 ,
                    textColor:   '#FBBF24',
                    strokeColor: '#FBBF24'    
                });
        }

        // Country label
        g.append("text")
            .attr("x", -10).attr("y", y(d.country) + y.bandwidth() / 2)
            .attr("fill", isIndo ? COLORS.red : COLORS.textDim)
            .attr("font-size", "12px")
            .attr("font-weight", isIndo ? "bold" : "normal")
            .attr("text-anchor", "end")
            .attr("alignment-baseline", "middle")
            .text(d.country);
    });
}

// ─────────────────────────────────────────────
// SECTION 4 — Radar Charts
// ─────────────────────────────────────────────
function renderSection4(fpData) {
    const CONSTRUCTS = {
        'AI Literacy'         : ['L1','L2','L3','L4','L5'],
        'AI Readiness'        : ['RE1','RE2','RE3','RE4','RE5','RE6'],
        'Relevance of AI'     : ['R1','R2','R3','R4','R5','R6'],
        'Career Motivation'   : ['CM1','CM2','CM3','CM4'],
        'Confidence'          : ['C1','C2','C3','C4','C5'],
        'Social Goods'        : ['SG1','SG2','SG3','SG4','SG5'],
        'Intrinsic Motivation': ['IM1','IM2','IM3','IM4'],
        'Satisfaction'        : ['S1','S2','S3','S4','S5'],
        'AI Anxiety'          : ['A1','A2','A3','A4','A5'],
        'Behavioural Intention': ['BI1','BI2','BI3','BI4','BI5'],
    };

    const COUNTRY_NAMES = {
        'SK':'Slovakia','PL':'Poland','CZ':'Czech Republic',
        'ID':'Indonesia','LT':'Lithuania','TR':'Turkey','FR':'France','UA':'Ukraine',
    };

    let rows = [];
    let grouped = d3.group(fpData, d => d.Country);
    for (let [code, grp] of grouped) {
        let row = { code, country: COUNTRY_NAMES[code] || code, n: grp.length };
        for (let construct in CONSTRUCTS) {
            let cols = CONSTRUCTS[construct];
            let constructSum = 0, constructCount = 0;
            cols.forEach(c => {
                let colSum = 0, colCount = 0;
                grp.forEach(d => {
                    let val = parseFloat(d[c]);
                    if (!isNaN(val) && val !== 0) { colSum += val; colCount++; }
                });
                if (colCount > 0) { constructSum += (colSum / colCount); constructCount++; }
            });
            row[construct] = constructCount > 0 ? (constructSum / constructCount) : 0;
        }
        rows.push(row);
    }

    rows = rows.filter(d => d.n >= 30);
    rows.forEach(d => { d['Low Anxiety'] = 6 - d['AI Anxiety']; });

    let idn_row      = rows.find(d => d.country === 'Indonesia') || {};
    let eur_countries = ['Slovakia','Poland','Czech Republic','Lithuania'];
    let eur_rows     = rows.filter(d => eur_countries.includes(d.country));

    const RADAR_AXES = ['AI Literacy','AI Readiness','Confidence',
                        'Career Motivation','Behavioural Intention','Low Anxiety'];

    let eur_vals = {};
    RADAR_AXES.forEach(ax => {
        let sum = d3.sum(eur_rows, d => d[ax]);
        eur_vals[ax] = eur_rows.length ? (sum / eur_rows.length) : 0;
    });

    const idn_radar  = RADAR_AXES.map(ax => idn_row[ax] || 0);
    const adv_radar  = RADAR_AXES.map(ax => eur_vals[ax] || 0);
    const ideal_radar = [4.3, 4.3, 4.3, 4.3, 4.3, 4.3];
    const labels = ['AI Literacy','AI Readiness','Confidence','Career Motiv.','Intent','Low Anxiety'];

    function createRadar(ctxId, dataVals, label, color, dash = []) {
        new Chart(document.getElementById(ctxId), {
            type: 'radar',
            data: {
                labels,
                datasets: [{
                    label,
                    data: dataVals,
                    backgroundColor: color + '40',
                    borderColor: color,
                    borderWidth: 2,
                    borderDash: dash,
                    pointBackgroundColor: color,
                    pointRadius: 0
                }]
            },
            options: {
                maintainAspectRatio: false,
                scales: {
                    r: {
                        min: 1, max: 5,
                        angleLines: { color: COLORS.muted },
                        grid: { color: COLORS.muted },
                        pointLabels: { color: COLORS.textDim, font: { size: 11, family: 'Inter' } },
                        ticks: { display: false, stepSize: 1 }
                    }
                },
                plugins: {
                    legend: { display: false },
                    title: {
                        display: true,
                        text: label,
                        color,
                        font: { size: 16, weight: 'bold', family: 'Inter' }
                    }
                }
            }
        });
    }

    createRadar('radar1', idn_radar,   'Indonesia',     COLORS.red);
    createRadar('radar2', adv_radar,   'European Avg',  COLORS.blue);
    createRadar('radar3', ideal_radar, 'Kondisi Ideal', COLORS.textDim, [5, 5]);
}