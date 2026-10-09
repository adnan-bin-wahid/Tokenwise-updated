"""Build editable draw.io report figures and geometry-matched SVG previews."""
from __future__ import annotations

import json
import textwrap
from pathlib import Path
from xml.etree import ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'reports' / 'figures'
PREVIEW = ROOT / 'tmp' / 'report-diagram-validation'
COLORS = {
    'process': ('#EAF2FA', '#315A7C'),
    'data': ('#E9F4EF', '#397259'),
    'external': ('#FFF4DC', '#916D29'),
    'note': ('#FFF8E9', '#AC8C48'),
    'error': ('#FDEDED', '#A54C4C'),
    'plain': ('#FFFFFF', '#586573'),
}
SVG = 'http://www.w3.org/2000/svg'
ET.register_namespace('', SVG)


class Figure:
    def __init__(self, number, title, subtitle, width, height):
        self.number, self.title = number, title
        self.width, self.height = width, height
        self.nodes, self.edges = {}, []
        self.model = ET.Element('mxGraphModel', {
            'dx': str(width), 'dy': str(height), 'grid': '1', 'gridSize': '10',
            'guides': '1', 'tooltips': '1', 'connect': '1', 'arrows': '1',
            'fold': '1', 'page': '1', 'pageScale': '1',
            'pageWidth': str(width), 'pageHeight': str(height),
            'math': '0', 'shadow': '0',
        })
        self.cells = ET.SubElement(self.model, 'root')
        ET.SubElement(self.cells, 'mxCell', {'id': '0'})
        ET.SubElement(self.cells, 'mxCell', {'id': '1', 'parent': '0'})
        self.node('title', f'Figure {number}. {title}', 40, 24, width - 80, 42,
                  kind='text', size=25, bold=True)
        self.node('subtitle', subtitle, 40, 72, width - 80, 38,
                  kind='text', size=15)

    def node(self, key, text, x, y, w, h, role='process', kind='box', size=16,
             bold=False, background=False):
        fill, stroke = COLORS[role]
        style = ('rounded=0;whiteSpace=wrap;html=0;fontFamily=Arial;'
                 f'fontSize={size};fontColor=#17212B;align=center;verticalAlign=middle;'
                 f'spacing=12;fillColor={fill};strokeColor={stroke};strokeWidth=1.5;')
        if bold:
            style += 'fontStyle=1;'
        if kind == 'text':
            style += 'text;fillColor=none;strokeColor=none;align=left;spacing=0;'
        elif kind == 'diamond':
            style += 'rhombus;spacing=4;'
        elif kind == 'store':
            style += 'shape=cylinder3;boundedLbl=1;backgroundOutline=1;size=14;'
        if background:
            style += 'fillColor=#F7F9FB;strokeColor=#BAC5CE;dashed=1;align=left;verticalAlign=top;spacing=18;fontStyle=1;'
        cell = ET.SubElement(self.cells, 'mxCell', {
            'id': key, 'value': text, 'style': style, 'vertex': '1', 'parent': '1',
        })
        ET.SubElement(cell, 'mxGeometry', {
            'x': str(x), 'y': str(y), 'width': str(w), 'height': str(h), 'as': 'geometry',
        })
        self.nodes[key] = dict(text=text, x=x, y=y, w=w, h=h, role=role,
                               kind=kind, size=size, bold=bold, background=background)
        return key

    def anchor(self, key, side):
        n = self.nodes[key]
        positions = {'L': (0, .5), 'R': (1, .5), 'T': (.5, 0), 'B': (.5, 1)}
        a, b = positions[side]
        return n['x'] + n['w'] * a, n['y'] + n['h'] * b

    def edge(self, source, target, label='', start='R', end='L', points=None,
             dashed=False, label_at=None, direct=False):
        a, b = self.anchor(source, start), self.anchor(target, end)
        self.line(a, b, label, points, dashed, label_at, source, target, start, end, direct)

    def line(self, a, b, label='', points=None, dashed=False, label_at=None,
             source=None, target=None, start='R', end='L', direct=False):
        points = points or []
        if not points and not direct and a[0] != b[0] and a[1] != b[1]:
            if start in ('T', 'B'):
                middle = (a[1] + b[1]) / 2
                points = [(a[0], middle), (b[0], middle)]
            else:
                middle = (a[0] + b[0]) / 2
                points = [(middle, a[1]), (middle, b[1])]
        key = f'edge-{len(self.edges) + 1}'
        style = ('edgeStyle=segmentEdgeStyle;rounded=0;html=0;endArrow=block;'
                 'endFill=1;strokeColor=#526170;strokeWidth=1.5;'
                 'fontFamily=Arial;fontSize=14;fontColor=#293746;labelBackgroundColor=#FFFFFF;')
        if dashed:
            style += 'dashed=1;'
        attrs = {'id': key, 'value': '' if label_at else label, 'style': style, 'edge': '1', 'parent': '1'}
        if source:
            port = {'L': (0, .5), 'R': (1, .5), 'T': (.5, 0), 'B': (.5, 1)}
            sx, sy = port[start]
            tx, ty = port[end]
            attrs.update(source=source, target=target)
            attrs['style'] += f'exitX={sx};exitY={sy};exitPerimeter=1;entryX={tx};entryY={ty};entryPerimeter=1;'
        cell = ET.SubElement(self.cells, 'mxCell', attrs)
        geometry = ET.SubElement(cell, 'mxGeometry', {'relative': '1', 'as': 'geometry'})
        if not source:
            for name, point in [('sourcePoint', a), ('targetPoint', b)]:
                ET.SubElement(geometry, 'mxPoint', {'x': str(point[0]), 'y': str(point[1]), 'as': name})
        if points:
            array = ET.SubElement(geometry, 'Array', {'as': 'points'})
            for x, y in points:
                ET.SubElement(array, 'mxPoint', {'x': str(x), 'y': str(y)})
        self.edges.append(dict(a=a, b=b, points=points, dashed=dashed, label=label, label_at=label_at))
        if label and label_at:
            x, y, w, h = label_at
            self.node(key + '-label', label, x, y, w, h, kind='text', size=14)

    def preview(self, path):
        svg = ET.Element(f'{{{SVG}}}svg', {'width': str(self.width), 'height': str(self.height),
                                         'viewBox': f'0 0 {self.width} {self.height}'})
        defs = ET.SubElement(svg, 'defs')
        marker = ET.SubElement(defs, 'marker', {'id': 'arrow', 'viewBox': '0 0 10 10',
                    'refX': '9', 'refY': '5', 'markerWidth': '7', 'markerHeight': '7', 'orient': 'auto'})
        ET.SubElement(marker, 'path', {'d': 'M 0 0 L 10 5 L 0 10 z', 'fill': '#526170'})
        ET.SubElement(svg, 'rect', {'width': '100%', 'height': '100%', 'fill': 'white'})

        def shape(n):
            x, y, w, h = n['x'], n['y'], n['w'], n['h']
            fill, stroke = COLORS[n['role']]
            if n['background']:
                fill, stroke = '#F7F9FB', '#BAC5CE'
            attrs = {'fill': fill, 'stroke': stroke, 'stroke-width': '1.5'}
            if n['background']:
                attrs['stroke-dasharray'] = '6 4'
            if n['kind'] == 'diamond':
                ET.SubElement(svg, 'polygon', {**attrs, 'points': f'{x+w/2},{y} {x+w},{y+h/2} {x+w/2},{y+h} {x},{y+h/2}'})
            elif n['kind'] != 'text':
                ET.SubElement(svg, 'rect', {**attrs, 'x': str(x), 'y': str(y), 'width': str(w), 'height': str(h)})
                if n['kind'] == 'store':
                    ET.SubElement(svg, 'path', {'d': f'M {x} {y+14} Q {x+w/2} {y+36} {x+w} {y+14}',
                                               'fill': 'none', 'stroke': stroke})

        for n in self.nodes.values():
            if n['background']:
                shape(n)
        for e in self.edges:
            points = [e['a'], *e['points'], e['b']]
            attrs = {'points': ' '.join(f'{x},{y}' for x, y in points), 'fill': 'none',
                     'stroke': '#526170', 'stroke-width': '1.5', 'marker-end': 'url(#arrow)'}
            if e.get('lifeline'):
                attrs.pop('marker-end')
            if e['dashed']:
                attrs['stroke-dasharray'] = '6 4'
            ET.SubElement(svg, 'polyline', attrs)
        for n in self.nodes.values():
            if not n['background']:
                shape(n)
            size = n['size']
            capacity = max(12, int((n['w'] - 24) / (size * .54)))
            lines = []
            for line in n['text'].split('\n'):
                lines.extend(textwrap.wrap(line, capacity, break_long_words=False, break_on_hyphens=False) or [''])
            left = n['kind'] == 'text' or n['background']
            tx = n['x'] + (18 if n['background'] else 0) if left else n['x'] + n['w']/2
            ty = n['y'] + 27 if n['background'] else n['y'] + n['h']/2 - (len(lines)-1)*size*.65 + size*.35
            attrs = {'x': str(tx), 'y': str(ty), 'font-family': 'Arial, sans-serif',
                     'font-size': str(size), 'fill': '#17212B', 'text-anchor': 'start' if left else 'middle'}
            if n['bold'] or n['background']:
                attrs['font-weight'] = 'bold'
            text = ET.SubElement(svg, 'text', attrs)
            for i, line in enumerate(lines):
                ET.SubElement(text, 'tspan', {'x': str(tx), 'dy': '0' if i == 0 else str(size*1.3)}).text = line
        for e in self.edges:
            if e['label'] and not e['label_at']:
                points = [e['a'], *e['points'], e['b']]
                a, b = points[len(points)//2-1:len(points)//2+1]
                x, y = (a[0]+b[0])/2, (a[1]+b[1])/2 - 9
                ET.SubElement(svg, 'rect', {'x': str(x-len(e['label'])*3.8), 'y': str(y-14),
                    'width': str(len(e['label'])*7.6), 'height': '20', 'fill': 'white'})
                ET.SubElement(svg, 'text', {'x': str(x), 'y': str(y), 'text-anchor': 'middle',
                    'font-family': 'Arial', 'font-size': '14', 'fill': '#293746'}).text = e['label']
        ET.ElementTree(svg).write(path, encoding='utf-8', xml_declaration=True)


def architecture():
    f = Figure(1, 'TokenWise runtime architecture and processing boundaries',
               'Local context preparation is distinct from downstream model inference and initial asset downloads.', 1660, 1160)
    f.node('local', 'LOCAL MACHINE | trusted editor workspace + loopback services', 40, 125, 1100, 870, background=True)
    f.node('remote', 'EXTERNAL SERVICES', 1190, 125, 430, 870, background=True)
    f.node('developer', 'Developer\nProgramming task', 85, 205, 215, 95, role='plain')
    f.node('agent', 'Antigravity editor / agent\nTools, workspace rules,\nfinal answer and authorized edits', 395, 190, 360, 130)
    f.node('cloud', 'Downstream model provider\nAgent-supplied prompt, context\nand native tool results', 1230, 190, 345, 130, role='external')
    f.node('extension', 'TokenWise TypeScript extension\nSetup, commands, file watchers,\nstatus and result webview', 85, 385, 365, 140)
    f.node('adapter', 'Automatic-context adapter\nSupported hook OR\nrule-followed command launcher', 600, 385, 470, 140)
    f.node('backend', 'Local FastAPI backend\nLoopback HTTP\nHealth, workspace pruning, indexing', 600, 620, 470, 115)
    f.node('repository', 'Local Python repository\nSource, tests and documents\nSaved file-change events', 85, 610, 365, 125, role='data', kind='store')
    f.node('pipeline', 'Context preparation\nAST index + lexical / graph retrieval\nNeural / structural reduction\nBudget packing + response guidance', 595, 795, 490, 150)
    f.node('managed', 'Managed runtime and assets\nCentral registration, environment,\ncheckpoint / tokenizer, carbon artifacts', 85, 795, 365, 150, role='data', kind='store')
    f.node('downloads', 'Initial dependency / model hosts\nVersioned packages, checkpoint,\ntokenizer and installer assets', 1230, 430, 345, 130, role='external')
    f.node('goalhost', 'Optional goal-generation endpoint\nOnly when explicitly configured\nDeterministic compiler is default', 1230, 705, 345, 130, role='external')
    f.edge('developer', 'agent', 'prompt')
    f.edge('agent', 'cloud', 'agent-managed model request')
    f.edge('agent', 'adapter', 'invoke', start='B', end='T')
    f.edge('extension', 'adapter', 'configure rules / launchers')
    f.edge('adapter', 'backend', 'POST /prune-workspace', start='B', end='T')
    f.edge('repository', 'backend', 'indexed source')
    f.edge('extension', 'backend', 'index / estimate / compare', start='R', end='L',
           points=[(500, 455), (500, 677)], label_at=(460, 546, 270, 32))
    f.edge('backend', 'pipeline', 'prepare packet', start='B', end='T')
    f.edge('managed', 'pipeline', 'local model / estimator assets')
    f.edge('downloads', 'managed', '', start='R', end='B', dashed=True,
           points=[(1595, 495), (1595, 1040), (267, 1040)])
    f.node('downloadlabel', 'Initial setup downloads (not per-prompt repository upload)', 440, 1008, 740, 30, kind='text', size=14)
    f.edge('backend', 'goalhost', 'opt-in generation', dashed=True)
    f.node('boundary', 'The adapter returns a bounded packet to the agent. Carbon / comparison updates enrich the local result separately.\nContext preparation is local; Antigravity can transmit supplied excerpts to its configured model provider.',
           40, 1070, 1580, 70, role='note', size=16)
    return f


def activity():
    f = Figure(2, 'Task-to-context activity flow and the separate overview path',
               'Input scope and task intent determine retrieval and reduction; the entire outgoing packet is budgeted.', 1580, 1440)
    f.node('input', 'Current task + workspace\nOptional selected file / exact excerpt\nBounded same-chat user references', 570, 135, 440, 110)
    f.node('goal', 'Compile structured goal\nTask type, identifiers, scope, constraints\nDeterministic default; optional generator', 570, 285, 440, 110)
    f.node('index', 'Repository index / search caches\nAST, symbols, imports, fingerprints\nIncremental saves + reconciliation', 65, 305, 345, 110, role='data', kind='store')
    f.node('decision', 'Repository\noverview task?', 665, 435, 250, 110, kind='diamond', size=17)
    f.node('focused', 'Focused retrieval / captured scope\nLexical + graph candidates and tests\nExplicit topic / exclusion filters', 160, 595, 450, 115)
    f.node('overview', 'Overview evidence selection\nProject documents + repository map\nRepresentative component source', 970, 595, 450, 115, role='data')
    f.node('reduce', 'Task-appropriate reduction\nNeural line scoring / threshold OR\nstructural / interface representation', 160, 765, 450, 115)
    f.node('overviewpack', 'Overview representations\nDistribute budget across components\nNo neural line pruning', 970, 765, 450, 115, role='data')
    f.node('pack', 'Pack the complete reference packet\nTask-aware response guidance + selected memory\nExcerpts, metadata and omission warnings\nCount complete packet; enforce token budget', 510, 965, 560, 145)
    f.node('record', 'Record automatic activity\nEvent, task, timestamp, scope, status and trace', 510, 1155, 560, 85, role='data')
    f.node('deliver', 'Deliver to Antigravity\nSupported hook context OR command tool output', 510, 1285, 560, 85)
    f.edge('input', 'goal', start='B', end='T')
    f.edge('goal', 'decision', start='B', end='T')
    f.edge('decision', 'focused', 'No: focused task', start='L', end='T', points=[(385, 490)], label_at=(405, 445, 230, 28))
    f.edge('decision', 'overview', 'Yes: broad overview', start='R', end='T', points=[(1195, 490)], label_at=(950, 445, 240, 28))
    f.edge('index', 'focused', 'indexed candidates', start='B', end='L', points=[(90, 455), (90, 652)], label_at=(130, 490, 270, 28))
    f.edge('index', 'overview', '', start='T', end='T', points=[(237, 115), (1480, 115), (1480, 560), (1195, 560)], dashed=True)
    f.node('indexlabel', 'Shared indexed map / metadata', 1090, 120, 385, 28, kind='text', size=14)
    f.edge('focused', 'reduce', start='B', end='T')
    f.edge('overview', 'overviewpack', start='B', end='T')
    f.edge('reduce', 'pack', start='B', end='L', points=[(385, 1037)])
    f.edge('overviewpack', 'pack', start='B', end='R', points=[(1195, 1037)])
    f.edge('pack', 'record', start='B', end='T')
    f.edge('record', 'deliver', start='B', end='T')
    f.node('fail', 'Invalid scope, missing readiness or processing failure\nExplicit error / unavailable state; no fabricated result', 70, 1155, 345, 115, role='error', size=15)
    f.edge('pack', 'fail', 'failure', start='L', end='T', points=[(450, 1037), (450, 1125), (242, 1125)], dashed=True)
    f.node('limit', 'Excerpts may omit evidence. The agent must read originals before edits.\nOverview coverage and scaffold-only source are disclosed.', 1135, 1180, 355, 135, role='note', size=15)
    return f


def ownership():
    f = Figure(3, 'Repository metadata, cache, and owned-file relationships',
               'File ownership and in-memory snapshots, not a relational database schema.', 1720, 1230)
    f.node('managedgroup', 'CENTRALLY MANAGED EDITOR STORAGE', 40, 125, 735, 390, background=True)
    f.node('workspacegroup', 'PER CONFIGURED PYTHON WORKSPACE', 825, 125, 855, 600, background=True)
    f.node('cachegroup', 'LOCAL SOURCE + IN-MEMORY BACKEND CACHES', 40, 565, 735, 585, background=True)
    f.node('researchgroup', 'RESEARCH ARTIFACTS | separate from runtime state', 825, 780, 855, 370, background=True)
    f.node('registration', 'backend/installation.json\nVerified backend registration\n(project root + launch metadata)', 80, 205, 295, 110, role='data', kind='store', size=15)
    f.node('runtime', 'Managed backend environment\nPinned checkpoint / tokenizer\nCarbon model registry + artifacts', 440, 205, 295, 110, role='data', kind='store', size=15)
    f.node('registry', 'Workspace ownership / cleanup records\nRegistered workspaces, content hashes, process identity\nModified / unrelated user resources are preserved', 80, 385, 655, 95, role='data', size=15)
    f.node('link', '.tokenwise/backend-link.json\nregistration_path\nResolves the central backend', 865, 205, 320, 110, role='data', kind='store', size=15)
    f.node('integration', 'Owned / merged .agents files\nrules/tokenwise*.md\ntokenwise.json + hooks.json\ntokenwise/ launchers', 1270, 205, 365, 165, role='data', size=15)
    f.node('manifest', '.agents/tokenwise/setup.json\nOwned filenames + hashes\nCleanup / merge metadata', 865, 390, 320, 105, role='data', size=15)
    f.node('activity', '.tokenwise/latest.json\nLatest event / task / time / status\nResult, provenance and packet', 865, 575, 320, 110, role='data', kind='store', size=15)
    f.node('history', '.tokenwise/conversations/\nConversation-scoped user state\nBounded references, not all chat\nAgent-command path can supply turns', 1270, 500, 365, 155, role='data', size=15)
    f.node('source', 'Python files / tests / documents\nContent fingerprints\nSave / create / delete / rename', 80, 645, 295, 110, role='plain', size=15)
    f.node('ast', 'Repository index snapshot\nAST + symbols / signatures\nImports, calls and token metadata', 440, 645, 295, 110, role='data', size=15)
    f.node('lexical', 'Lexical search cache\nTerms / counts / postings\nInvalidate changed source only', 80, 835, 295, 100, role='data', size=15)
    f.node('graph', 'Dependency / symbol cache\nRelationships and reverse links\nRebuild affected metadata', 440, 835, 295, 100, role='data', size=15)
    f.node('exact', 'Exact context-result cache\nQuery + scope / settings + snapshot fingerprint\nSource change invalidates reuse; reconcile missed events', 80, 1020, 655, 95, role='data', size=15)
    f.node('evaluation', 'evaluation/comparative-study/\nPinned cases + snapshots + results\nmetrics.csv + summaries / tables', 865, 865, 340, 130, role='plain', size=15)
    f.node('validation', 'evaluation/test-validation/\nSoftware test records\nBrowser fixture checks', 1270, 865, 365, 130, role='plain', size=15)
    f.node('researchnote', 'Recorded research is not live activity, provider token usage or measured emissions.\nNo PostgreSQL / relational database is required by the normal runtime.', 865, 1040, 770, 80, role='note', size=15)
    f.edge('link', 'registration', 'references registration_path', start='L', end='B',
           points=[(800, 260), (800, 350), (227, 350)], label_at=(460, 316, 320, 28))
    f.edge('runtime', 'registration', start='L', end='R')
    f.edge('registry', 'manifest', 'ownership / cleanup', start='R', end='L')
    f.edge('manifest', 'integration', 'files + hashes', start='R', end='B', points=[(1230, 442), (1452, 442)])
    f.edge('source', 'ast', 'parse / fingerprint')
    f.edge('ast', 'graph', 'relationships', start='B', end='T')
    f.edge('ast', 'lexical', 'search features', start='L', end='T', points=[(407, 700), (407, 795), (227, 795)])
    f.edge('lexical', 'exact', '', start='B', end='T', points=[(227, 975), (407, 975)])
    f.edge('graph', 'exact', 'snapshot-keyed reuse', start='B', end='T', points=[(587, 975), (407, 975)], label_at=(450, 980, 270, 28))
    f.node('historynote', 'Memory references are selected before packet packing;\nassistant and tool output are not retained as user intent.', 855, 725, 780, 40, kind='text', size=14)
    return f


def sequence():
    f = Figure(4, 'Automatic prompt retrieval and asynchronous result enrichment',
               'Illustrative event order: agent work and optional enrichment can overlap. Hook support, trust and tool permissions matter.', 1840, 1370)
    centers = [150, 455, 760, 1065, 1370, 1675]
    labels = ['Developer', 'Antigravity\nagent', 'Hook / command\nadapter', 'Local FastAPI\nbackend', 'Workspace activity\nlatest.json', 'Extension monitor\n+ result panel']
    f.node('async', 'INDEPENDENT ENRICHMENT | may overlap steps 6-7; delivery does not wait; prepared comparison avoids a second neural prune',
           40, 825, 1760, 345, background=True, size=15)
    for i, (x, label) in enumerate(zip(centers, labels)):
        f.node(f'participant-{i}', label, x-125, 130, 250, 75, role='data' if i == 4 else 'process', size=16, bold=True)
        # Lifelines are native editable edges with no arrowheads.
        f.line((x, 205), (x, 1185), dashed=True, direct=True)
        f.cells[-1].set('style', f.cells[-1].get('style').replace('endArrow=block', 'endArrow=none'))
        f.edges[-1]['lifeline'] = True

    def message(a, b, y, label, dashed=False):
        left, right = sorted([centers[a], centers[b]])
        f.line((centers[a], y), (centers[b], y), label, dashed=dashed, direct=True,
               label_at=(left+12, y-48, right-left-24, 40))

    message(0, 1, 250, '1. Submit programming request')
    message(1, 2, 320, '2. Supported hook OR rule-followed tool command')
    message(2, 3, 390, 'Health check / verified startup (if permitted)')
    message(2, 3, 460, '3. /prune-workspace: task, scope, user history')
    message(3, 2, 530, '4. Bounded packet + scope / pruning trace', True)
    message(2, 4, 600, '5. Write fresh ready activity: event, task, timestamp, result')
    message(2, 1, 670, '6. Hook context OR command stdout', True)
    message(1, 0, 740, '7. Continue answer / native tool work using packet', True)
    message(4, 5, 805, '8. Observe file change; validate freshness')
    message(5, 3, 915, '9a. /estimate-carbon (if enabled)')
    message(3, 5, 975, 'Phase / CO2 estimates OR unavailable / error', True)
    message(5, 3, 1050, '9b. /compare-prepared-workspace (if enabled)')
    message(3, 5, 1110, 'Same-snapshot result OR stale / oversized / error', True)
    f.node('refresh', 'Refresh statistics / comparison in result panel', 1125, 1175, 675, 40, kind='text', size=15)
    f.node('errors', 'FAILURE / PERMISSION BOUNDARIES\nDisabled setup, denied tool execution, backend unavailability or retrieval failure produce explicit error / no context.\nCarbon / comparison failure does not erase a prepared packet; unavailable measurements are not reported as zero.\nA local activity record proves preparation, not universal interception or verified cloud consumption.',
           40, 1230, 1760, 115, role='error', size=16)
    return f


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    PREVIEW.mkdir(parents=True, exist_ok=True)
    figures = [architecture(), activity(), ownership(), sequence()]
    file = ET.Element('mxfile', {'host': 'app.diagrams.net', 'agent': 'TokenWise report diagram builder',
                                'version': '24.7.17', 'type': 'device', 'compressed': 'false'})
    for f in figures:
        for key, node in f.nodes.items():
            assert node['x'] >= 0 and node['y'] >= 0, (f.number, key)
            assert node['x'] + node['w'] <= f.width, (f.number, key)
            assert node['y'] + node['h'] <= f.height, (f.number, key)
        diagram = ET.SubElement(file, 'diagram', {'id': f'tokenwise-figure-{f.number}',
                                                 'name': f'Figure {f.number} - {f.title}'})
        diagram.append(f.model)
        f.preview(PREVIEW / f'figure-{f.number}.svg')
    path = OUT / 'TokenWise_Figures_1-4.drawio'
    ET.indent(file, space='  ')
    ET.ElementTree(file).write(path, encoding='utf-8', xml_declaration=True)
    check = ET.parse(path).getroot()
    assert len(check.findall('diagram')) == 4
    for page in check.findall('diagram'):
        cells = page.findall('./mxGraphModel/root/mxCell')
        ids = [cell.get('id') for cell in cells]
        assert len(ids) == len(set(ids)), page.get('name')
        for cell in cells:
            for ref in ('parent', 'source', 'target'):
                assert cell.get(ref) is None or cell.get(ref) in ids, (cell.get('id'), ref)
    print(json.dumps({'file': str(path), 'pages': [f.title for f in figures],
                      'nodes': [len(f.nodes) for f in figures], 'edges': [len(f.edges) for f in figures]}, indent=2))


if __name__ == '__main__':
    main()
