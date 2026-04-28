// script.js
const COLORS = {
    bg: '#0D1B2E',
    panelBg: '#1E293B',
    textMain: '#F1F5F9',
    textDim: '#94A3B8',
    accent: '#FBBF24',
    red: '#E24B4A',
    muted: '#334155',
    blue: '#378ADD'
};

const COUNTRY_COLORS = {
    'Indonesia'     : '#E24B4A',
    'Singapore'     : '#5B9BD5',
    'Brazil'        : '#1D9E75',
    'India'         : '#E8A838',
    'United States' : '#60A5FA',
    'China'         : '#F87171',
    'Germany'       : '#A78BFA',
    'United Kingdom': '#34D399',
    'France'        : '#FB923C',
    'Finland'       : '#38BDF8',
    'Japan'         : '#F9A8D4',
    'South Korea'   : '#86EFAC',
    'Canada'        : '#67E8F9',
    'Australia'     : '#FCD34D',
};

const REGION_COLORS = {
    'Asia'     : '#7C3AED',
    'Europe'   : '#0891B2',
    'Americas' : '#059669',
    'Africa'   : '#D97706',
    'Oceania'  : '#BE185D',
    'Others'   : '#475569',
};

const PILLARS = [
    {key: 'ai_talent', label: 'Talent', color: '#818CF8'},
    {key: 'ai_infrastructure', label: 'Infrastructure', color: '#38BDF8'},
    {key: 'ai_government_strategy', label: 'Gov. Strategy', color: '#34D399'},
    {key: 'ai_research', label: 'Research', color: '#FBBF24'},
    {key: 'ai_development', label: 'Development', color: '#F472B6'},
    {key: 'ai_commercial', label: 'Commercial', color: '#FB923C'},
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
    if (COUNTRY_COLORS[country]) return COUNTRY_COLORS[country];
    if (REGION_COLORS[region]) return REGION_COLORS[region];
    return COLORS.muted;
}

Promise.all([
    d3.csv("ai_data.csv"),
    d3.csv("fitped_raw.csv")
]).then(([aiData, fpData]) => {

    // PRE-PROCESSING
    aiData.forEach(d => {
        // Lowercase and strip keys mapping to clean keys
        let cleanRow = {};
        for (let k in d) {
            let cln = k.trim().toLowerCase().replace(/ /g, '_');
            cleanRow[cln] = d[k];
        }
        Object.assign(d, cleanRow);
        
        d.ai_overall_score = +d.ai_overall_score;
        d.gdp_per_capita = +d.gdp_per_capita;
        if (isNaN(d.gdp_per_capita) || d.gdp_per_capita === 0) {
            if (d.country === 'South Korea') d.gdp_per_capita = 32000;
            else if (d.country === 'Egypt') d.gdp_per_capita = 3000;
            else d.gdp_per_capita = 5000;
        }
        d.ai_government_strategy = +d.ai_government_strategy;
        d.internet_usage_pct = +d.internet_usage_pct;
        d.region = REGION_MAP[d.country] || 'Others';
        PILLARS.forEach(p => {
            d[p.key] = +d[p.key] || 0;
        });
    });

    // We don't pre-cast fpData because raw columns might be strings and have NAs.
    // We will handle fpData processing inside renderSection4

    renderSection2(aiData);
    renderSection3(aiData);
    renderSection4(fpData);
});

function renderSection2(data) {
    // Top 12 + ASEAN + Peers
    let sortedGlobal = [...data].sort((a,b) => b.ai_overall_score - a.ai_overall_score);
    let top12 = sortedGlobal.slice(0, 12).map(d => d.country);
    let asean = ['Malaysia','Thailand','Indonesia','Vietnam','Philippines'];
    let peers = ['Brazil','India','Colombia','Egypt','Morocco','Nigeria','Mexico'];
    
    let selectedNames = new Set([...top12, ...asean, ...peers]);
    let df = data.filter(d => selectedNames.has(d.country));

    const REGION_ORDER = ['Americas','Asia','Europe','Africa','Oceania','Others'];
    df.sort((a, b) => {
        let riA = REGION_ORDER.indexOf(a.region);
        let riB = REGION_ORDER.indexOf(b.region);
        if (riA === -1) riA = 99;
        if (riB === -1) riB = 99;
        if (riA !== riB) return riA - riB;
        return b.gdp_per_capita - a.gdp_per_capita;
    });

    const N = df.length;
    const TOTAL_GDP = d3.sum(df, d => d.gdp_per_capita);

    // Setup SVG
    const container = document.getElementById("flow-charts");
    const width = container.clientWidth;
    const height = container.clientHeight;

    const svg = d3.select("#flow-charts")
        .append("svg")
        .attr("width", width)
        .attr("height", height);

    // Columns width ratios: Sankey(5.5), Bar(3.5), Bubble(1.5)
    const sankeyW = width * 0.52;
    const barW = width * 0.33;
    const bubW = width * 0.15;
    
    // Y Geometries
    const REGION_GAP = 50;
    
    // Left side y-centers (grouped by region, proportional to GDP)
    let regionsInOrder = [...new Set(df.map(d => d.region))];
    let gapBudget = regionsInOrder.length * REGION_GAP;
    let bandBudget = height - gapBudget - 40; // Total height allocated for GDP thickness

    df.forEach(d => {
        d.h = (d.gdp_per_capita / TOTAL_GDP) * bandBudget;
        // ensure minimum thickness so it's visible and text can fit
        if (d.h < 9) d.h = 9;
    });

    // Re-evaluate bandBudget because of minimums
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

    // Right side y-centers (evenly distributed gaps, but thickness is d.h)
    let rightGap = (height - 40 - actualBandTotal) / (N - 1);
    let rightCurY = height - 20;
    df.slice().reverse().forEach(d => {
        d.right_yb = rightCurY;
        d.right_yt = rightCurY - d.h;
        d.right_yc = rightCurY - d.h / 2;
        rightCurY -= (d.h + rightGap);
    });

    // DRAW SANKEY
    const sankeyLeftMargin = 160; // Make room for country and region labels
    const sankeyG = svg.append("g").attr("transform", `translate(${sankeyLeftMargin},0)`);
    const sankeyInnerW = sankeyW - sankeyLeftMargin;

    // Draw region labels and brackets
    regionsInOrder.forEach(reg => {
        let regRows = df.filter(d => d.region === reg);
        let topY = d3.min(regRows, d => d.left_yt);
        let botY = d3.max(regRows, d => d.left_yb);
        let midY = (topY + botY) / 2;
        let rc = REGION_COLORS[reg] || COLORS.muted;

        sankeyG.append("line")
            .attr("x1", -30) // Moved closer to band (was -80)
            .attr("x2", -30)
            .attr("y1", botY)
            .attr("y2", topY)
            .attr("stroke", rc)
            .attr("stroke-width", 4)
            .attr("stroke-linecap", "round");

        sankeyG.append("text")
            .attr("x", -40) // Moved closer to bracket (was -90)
            .attr("y", midY)
            .attr("fill", rc)
            .attr("font-size", "13px")
            .attr("font-weight", "800")
            .attr("text-anchor", "end")
            .attr("alignment-baseline", "middle")
            .style("letter-spacing", "2px")
            .text(reg.toUpperCase());
    });

    const tooltip = d3.select("#tooltip");

    df.forEach(d => {
        let xl = 0;
        let xr = sankeyInnerW;
        let c1 = xl + (xr - xl) * 0.4;
        let c2 = xl + (xr - xl) * 0.6;
        let col = getCountryColor(d.country, d.region);

        let pathData = `M ${xl} ${d.left_yb} 
                        C ${c1} ${d.left_yb}, ${c2} ${d.right_yb}, ${xr} ${d.right_yb}
                        L ${xr} ${d.right_yt}
                        C ${c2} ${d.right_yt}, ${c1} ${d.left_yt}, ${xl} ${d.left_yt} Z`;

        let band = sankeyG.append("path")
            .attr("d", pathData)
            .attr("fill", col)
            .attr("opacity", 0.72)
            .attr("class", "sankey-link");

        band.on("mouseover", function(e) {
            d3.select(this).attr("opacity", 0.95);
            tooltip.style("opacity", 1)
                   .html(`<b>${d.country}</b><br>GDP: $${d.gdp_per_capita.toLocaleString()}<br>Gov Strategy: ${d.ai_government_strategy.toFixed(1)}`);
        }).on("mousemove", function(e) {
            tooltip.style("left", (e.pageX + 15) + "px")
                   .style("top", (e.pageY - 15) + "px");
        }).on("mouseout", function(e) {
            d3.select(this).attr("opacity", 0.72);
            tooltip.style("opacity", 0);
        });

        // Country Name inside the Sankey flow band (near the right edge)
        // Scale font size based on band height, but keep it readable (min 9px, max 12px)
        let fontSizeNum = Math.min(12, Math.max(9, d.h - 1));
        let fs = fontSizeNum + 'px';
        let fw = 'normal';
        
        // Country label
        sankeyG.append("text")
            .attr("x", xr - 15) // Place it on the flat part of the band right before it hits the bar chart
            .attr("y", d.right_yc)
            .attr("fill", "#F8FAFC") // Brighter color (slate-50) so it's highly visible
            .attr("font-size", fs)
            .attr("font-weight", fw)
            .attr("text-anchor", "end")
            .attr("alignment-baseline", "middle")
            .text(d.country);

        // Add GDP number if band is thick enough (e.g. > 14px)
        if (d.h > 14) {
            let gdpFormatted = `$${Math.round(d.gdp_per_capita / 1000)}k`;
            sankeyG.append("text")
                .attr("x", xl + 15) // near the left edge of the band
                .attr("y", d.left_yc)
                .attr("fill", "#334155") // matching dark gray
                .attr("font-size", "10px")
                .attr("font-weight", "700")
                .attr("text-anchor", "start")
                .attr("alignment-baseline", "middle")
                .text(gdpFormatted);
        }
    });

    // DRAW BAR (Connected perfectly to Sankey)
    const barG = svg.append("g").attr("transform", `translate(${sankeyLeftMargin + sankeyInnerW}, 0)`);
    const barInnerW = barW - 10;
    const maxBar = 100;
    const xScaleBar = d3.scaleLinear().domain([0, maxBar]).range([0, barInnerW]);

    df.forEach(d => {
        let col = getCountryColor(d.country, d.region);
        
        // Bar
        barG.append("rect")
            .attr("x", 0)
            .attr("y", d.right_yt)
            .attr("width", xScaleBar(d.ai_government_strategy))
            .attr("height", d.h) // match Sankey height perfectly
            .attr("fill", col)
            .attr("opacity", 0.88);

        // Value text
        barG.append("text")
            .attr("x", xScaleBar(d.ai_government_strategy) + 8)
            .attr("y", d.right_yc)
            .attr("fill", COLORS.textDim)
            .attr("font-size", "10px")
            .attr("alignment-baseline", "middle")
            .text(Math.round(d.ai_government_strategy));
    });

    // DRAW BUBBLE / SCORE
    const bubG = svg.append("g").attr("transform", `translate(${sankeyLeftMargin + sankeyInnerW + barInnerW + 40}, 0)`);
    const maxScore = d3.max(df, d => d.ai_overall_score);
    const radScale = d3.scaleSqrt().domain([0, maxScore]).range([3, 16]); // Fixed max radius to avoid overlaps with variable row heights

    df.forEach(d => {
        let col = getCountryColor(d.country, d.region);
        let r = radScale(d.ai_overall_score);
        
        bubG.append("circle")
            .attr("cx", bubW/2)
            .attr("cy", d.right_yc)
            .attr("r", r)
            .attr("fill", col)
            .attr("fill-opacity", 0.4)
            .attr("stroke", col)
            .attr("stroke-width", 2);
    });
}

function renderSection3(data) {
    const SUBSET_NAMES = ['United States','China','Singapore','United Kingdom','Germany',
                          'Finland','India','Brazil','Malaysia','Vietnam','Indonesia',
                          'Colombia','Nigeria'];
    
    let ds3 = [];
    SUBSET_NAMES.forEach(c => {
        let r = data.find(d => d.country === c);
        if (r) ds3.push(r);
    });

    // Legend
    const legendContainer = d3.select("#pillar-legend");
    PILLARS.forEach(p => {
        let item = legendContainer.append("div").attr("class", "legend-item");
        item.append("div").attr("class", "legend-color").style("background-color", p.color);
        item.append("div").text(p.label);
    });

    const container = document.getElementById("pillars-chart");
    const width = container.clientWidth;
    const height = container.clientHeight;

    const svg = d3.select("#pillars-chart")
        .append("svg")
        .attr("width", width)
        .attr("height", height);

    const margin = {top: 20, right: 20, bottom: 20, left: 100};
    const innerW = width - margin.left - margin.right;
    const innerH = height - margin.top - margin.bottom;

    const y = d3.scaleBand()
        .domain(ds3.map(d => d.country))
        .range([0, innerH])
        .padding(0.3);

    const x = d3.scaleLinear()
        .domain([0, 600]) // Max possible score across 6 pillars (each max 100)
        .range([0, innerW]);

    const g = svg.append("g").attr("transform", `translate(${margin.left},${margin.top})`);

    ds3.forEach(d => {
        let currentX = 0;
        
        PILLARS.forEach(p => {
            let val = d[p.key] || 0;
            g.append("rect")
                .attr("x", x(currentX))
                .attr("y", y(d.country))
                .attr("width", x(val))
                .attr("height", y.bandwidth())
                .attr("fill", p.color)
                .attr("opacity", 0.88);
            currentX += val;
        });

        // Label
        let fw = d.country === 'Indonesia' ? 'bold' : 'normal';
        let fc = d.country === 'Indonesia' ? COLORS.red : COLORS.textDim;
        
        g.append("text")
            .attr("x", -15)
            .attr("y", y(d.country) + y.bandwidth()/2)
            .attr("fill", fc)
            .attr("font-size", "12px")
            .attr("font-weight", fw)
            .attr("text-anchor", "end")
            .attr("alignment-baseline", "middle")
            .text(d.country);
            
        // Removed the confusing red empty border box for Indonesia
    });
}

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
        'SK': 'Slovakia', 'PL': 'Poland', 'CZ': 'Czech Republic',
        'ID': 'Indonesia', 'LT': 'Lithuania',
        'TR': 'Turkey',    'FR': 'France',  'UA': 'Ukraine',
    };

    let rows = [];
    // Group by Country
    let grouped = d3.group(fpData, d => d.Country);
    for (let [code, grp] of grouped) {
        let row = { code: code, country: COUNTRY_NAMES[code] || code, n: grp.length };
        for (let construct in CONSTRUCTS) {
            let cols = CONSTRUCTS[construct];
            let constructSum = 0;
            let constructCount = 0;
            // A bit of manual nested aggregation to match pandas mean(skipna=True).mean()
            cols.forEach(c => {
                let colSum = 0;
                let colCount = 0;
                grp.forEach(d => {
                    let val = parseFloat(d[c]);
                    if (!isNaN(val) && val !== 0) {
                        colSum += val;
                        colCount++;
                    }
                });
                if (colCount > 0) {
                    constructSum += (colSum / colCount);
                    constructCount++;
                }
            });
            row[construct] = constructCount > 0 ? (constructSum / constructCount) : 0;
        }
        rows.push(row);
    }

    // Filter eligible countries (n >= 30)
    rows = rows.filter(d => d.n >= 30);
    
    // Invert Anxiety
    rows.forEach(d => {
        d['Low Anxiety'] = 6 - d['AI Anxiety'];
    });

    let idn_row = rows.find(d => d.country === 'Indonesia') || {};
    let eur_countries = ['Slovakia','Poland','Czech Republic','Lithuania'];
    let eur_rows = rows.filter(d => eur_countries.includes(d.country));

    const RADAR_AXES = ['AI Literacy','AI Readiness','Confidence',
                        'Career Motivation','Behavioural Intention','Low Anxiety'];
    
    // Compute European average
    let eur_vals = {};
    RADAR_AXES.forEach(ax => {
        let sum = d3.sum(eur_rows, d => d[ax]);
        eur_vals[ax] = eur_rows.length ? (sum / eur_rows.length) : 0;
    });

    const idn_radar = RADAR_AXES.map(ax => idn_row[ax] || 0);
    const adv_radar = RADAR_AXES.map(ax => eur_vals[ax] || 0);
    const ideal_radar = [4.3, 4.2, 4.2, 4.1, 4.2, 4.0];
    
    const labels = ['AI Literacy', 'AI Readiness', 'Confidence', 'Career Motiv.', 'Intent', 'Low Anxiety'];

    function createRadar(ctxId, dataVals, label, color, dash = []) {
        new Chart(document.getElementById(ctxId), {
            type: 'radar',
            data: {
                labels: labels,
                datasets: [{
                    label: label,
                    data: dataVals,
                    backgroundColor: color + '40', // 25% opacity
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
                        angleLines: { color: COLORS.muted },
                        grid: { color: COLORS.muted },
                        pointLabels: { color: COLORS.textDim, font: { size: 11, family: 'Inter' } },
                        ticks: { display: false, min: 1, max: 5 }
                    }
                },
                plugins: {
                    legend: { display: false },
                    title: {
                        display: true,
                        text: label,
                        color: color,
                        font: { size: 16, weight: 'bold', family: 'Inter' }
                    }
                }
            }
        });
    }

    createRadar('radar1', idn_radar, 'Indonesia', COLORS.red);
    createRadar('radar2', adv_radar, 'European Avg', COLORS.blue);
    createRadar('radar3', ideal_radar, 'Kondisi Ideal', COLORS.textDim, [5, 5]);
}
