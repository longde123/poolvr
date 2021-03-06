"""
Flask application for serving poolvr.
"""
import os
import logging
import json
import shutil
import subprocess
from copy import deepcopy
from flask import Flask, request, Markup
from jinja2 import Environment, FileSystemLoader




_logger = logging.getLogger(__name__)
_here = os.path.dirname(os.path.abspath(__file__))
PACKAGE = json.loads(open('package.json').read())
STATIC_FOLDER   = _here
TEMPLATE_FOLDER = STATIC_FOLDER
DIST_OUTPUT_DIR = os.path.join(_here, 'dist')


GIT_REVS = []
try:
    completed_proc = subprocess.run(['git', 'rev-list', '--max-count=4', 'HEAD'], stdout=subprocess.PIPE, check=True, universal_newlines=True)
    for line in completed_proc.stdout.splitlines():
        GIT_REVS.append(line)
except Exception as err:
    _logger.warn('could not obtain git info:\n%s' % err)


app = Flask(__name__,
            static_folder=STATIC_FOLDER,
            static_url_path='',
            template_folder=TEMPLATE_FOLDER)


env = Environment(loader=FileSystemLoader(TEMPLATE_FOLDER))
template = env.get_template('poolvr_template.html')


WebVRConfig = {
    "FORCE_ENABLE_VR":                  False,
    "K_FILTER":                         0.98,
    "PREDICTION_TIME_S":                0.010,
    "TOUCH_PANNER_DISABLED":            False,
    "YAW_ONLY":                         False,
    "MOUSE_KEYBOARD_CONTROLS_DISABLED": False,
    "KEYBOARD_CONTROLS_DISABLED":       True
}


INCH2METER = 0.0254


POOLVR = {
    'version': PACKAGE['version'],
    'config': {
        'gravity'            : 9.81,
        'useBasicMaterials'  : True,
        'useShadowMap'       : False,
        'useSpotLight'       : True,
        'usePointLight'      : False,
        'useTextGeomLogger'  : True,
        'L_table'            : 2.3368,
        'H_table'            : 0.77,
        'ball_diameter'      : 2.25 * INCH2METER,
        'soundVolume'        : 0.0,
        'toolOptions': {
            'tipShape'               : 'Cylinder',
            'numSegments'            : 8,
            'toolRadius'             : 0.009, #0.01325 / 2,
            'tipRadius'              : 0.009, #0.01325 / 2,
            'toolLength'             : 0.37,
            'tipLength'              : 0.37,
            'toolMass'               : 0.54,
            'offset'                 : [0, 0, 0.37 / 2],
            'interactionPlaneOpacity': 0.22,
            'useImplicitCylinder'    : True
        }
    }
}


def get_webvr_config():
    """
    Constructs WebVRConfig dict based on request url parameters.
    """
    config = deepcopy(WebVRConfig)
    args = dict({k: v for k, v in request.args.items()
                 if k in config})
    for k, v in args.items():
        if v == 'false':
            args[k] = False
        elif v == 'true':
            args[k] = True
        elif not (v is False or v is True or v is None):
            try:
                args[k] = float(v)
            except Exception as err:
                _logger.warning(err)
    config.update(args)
    return config


def get_poolvr_config():
    """
    Constructs poolvr config dict based on request url parameters.
    """
    config = deepcopy(POOLVR['config'])
    args = dict({k: v for k, v in request.args.items()
                 if k in config})
    for k, v in args.items():
        if v == 'false':
            args[k] = False
        elif v == 'true':
            args[k] = True
        elif not (v is None):
            try:
                args[k] = float(v)
            except Exception as err:
                _logger.warning(err)
    config.update(args)
    return {'config': config,
            'version': POOLVR['version']}


def render_poolvr_template(webvr_config=None, poolvr_config=None):
    import pool_table
    if webvr_config is None:
        webvr_config = WebVRConfig
    if poolvr_config is None:
        poolvr_config = POOLVR
    return template.render(config={'DEBUG': app.debug},
                           json_config=Markup(r"""<script>
var WebVRConfig = %s;
var POOLVR = %s;
var THREEPY_SCENE = %s;
</script>""" % (json.dumps(webvr_config, indent=2),
                json.dumps(poolvr_config, indent=2),
                json.dumps(pool_table.pool_hall(**poolvr_config['config']).export()))),
                           version=poolvr_config['version'],
                           version_content=Markup(r"""
<table>
<tr>
<td>
<a href="https://github.com/jzitelli/poolvr/commit/{0}">current commit ({3})</a>
</td>
</tr>
<tr>
<td>
<a href="https://github.com/jzitelli/poolvr/commit/{1}">previous commit ({4})</a>
</td>
</tr>
</table>
""".format(GIT_REVS[0], GIT_REVS[1], poolvr_config['version'], '%s...' % GIT_REVS[0][:6], '%s...' % GIT_REVS[1][:6])) if GIT_REVS else None)


@app.route('/')
def poolvr():
    """
    Serves the poolvr app HTML.
    """
    webvr_config = get_webvr_config()
    poolvr_config = get_poolvr_config()
    return render_poolvr_template(webvr_config=webvr_config, poolvr_config=poolvr_config)


def main():
    werkzeug_logger = logging.getLogger('werkzeug')
    werkzeug_logger.setLevel(logging.WARNING)
    # werkzeug_logger.disabled = True
    _logger.info("""


           ***********
           p o o l v r
    *************************
              {0}
 *******************************
 STARTING FLASK APP!!!!!!!!!!!!!
 *******************************
              {0}
    *************************
           p o o l v r
           ***********

""".format(POOLVR['version']))
    PORT = 5000
    # _logger.debug("app.config =\n%s" % '\n'.join(['  %s: %s' % (k, str(v))
    #                                               for k, v in sorted(app.config.items(),
    #                                                                  key=lambda i: i[0])]))
    _logger.info("""


        GO TO:

            http://127.0.0.1:%d


""" % PORT)
    app.run(host='0.0.0.0', port=PORT)


def make_dist():
    _logger.info('building distributable version, output directory: "%s"...', DIST_OUTPUT_DIR)
    shutil.rmtree(DIST_OUTPUT_DIR, ignore_errors=True)
    shutil.copytree('build', os.path.join(DIST_OUTPUT_DIR, 'build'))
    html_path = os.path.join(DIST_OUTPUT_DIR, 'poolvr.html')
    with open(html_path, 'w') as f:
        f.write(render_poolvr_template())
    # copy resources:
    shutil.copy('poolvr.css', DIST_OUTPUT_DIR)
    shutil.copy('favicon.ico', DIST_OUTPUT_DIR)
    shutil.copytree('fonts', os.path.join(DIST_OUTPUT_DIR, 'fonts'))
    shutil.copytree('images', os.path.join(DIST_OUTPUT_DIR, 'images'))
    shutil.copytree('sounds', os.path.join(DIST_OUTPUT_DIR, 'sounds'))
    # copy npm dependencies:
    shutil.copytree(os.path.join('node_modules', 'cannon', 'build'), os.path.join(DIST_OUTPUT_DIR, 'node_modules', 'cannon', 'build'))
    os.makedirs(os.path.join(DIST_OUTPUT_DIR, 'node_modules', 'leapjs'))
    shutil.copy(os.path.join('node_modules', 'leapjs', 'leap-0.6.4.min.js'), os.path.join(DIST_OUTPUT_DIR, 'node_modules', 'leapjs'))
    os.makedirs(os.path.join(DIST_OUTPUT_DIR, 'node_modules', 'three', 'build'))
    shutil.copy(os.path.join('node_modules', 'three', 'build', 'three.js'), os.path.join(DIST_OUTPUT_DIR, 'node_modules', 'three', 'build'))
    shutil.copy(os.path.join('node_modules', 'three', 'build', 'three.min.js'), os.path.join(DIST_OUTPUT_DIR, 'node_modules', 'three', 'build'))
    os.makedirs(os.path.join(DIST_OUTPUT_DIR, 'node_modules', 'three', 'examples', 'js', 'controls'))
    os.makedirs(os.path.join(DIST_OUTPUT_DIR, 'node_modules', 'three', 'examples', 'js', 'effects'))
    os.makedirs(os.path.join(DIST_OUTPUT_DIR, 'node_modules', 'three', 'examples', 'js', 'objects'))
    os.makedirs(os.path.join(DIST_OUTPUT_DIR, 'node_modules', 'three', 'examples', 'js', 'loaders'))
    shutil.copy(os.path.join('node_modules', 'three', 'examples', 'js', 'controls', 'VRControls.js'), os.path.join(DIST_OUTPUT_DIR, 'node_modules', 'three', 'examples', 'js', 'controls'))
    shutil.copy(os.path.join('node_modules', 'three', 'examples', 'js', 'effects', 'VREffect.js'), os.path.join(DIST_OUTPUT_DIR, 'node_modules', 'three', 'examples', 'js', 'effects'))
    shutil.copy(os.path.join('node_modules', 'three', 'examples', 'js', 'objects', 'ShadowMesh.js'), os.path.join(DIST_OUTPUT_DIR, 'node_modules', 'three', 'examples', 'js', 'objects'))
    shutil.copy(os.path.join('node_modules', 'three', 'examples', 'js', 'loaders', 'OBJLoader.js'), os.path.join(DIST_OUTPUT_DIR, 'node_modules', 'three', 'examples', 'js', 'loaders'))
    shutil.copytree(os.path.join('node_modules', 'three', 'examples', 'models'), os.path.join(os.path.join(DIST_OUTPUT_DIR, 'node_modules', 'three', 'examples', 'models')))
    shutil.copytree(os.path.join('node_modules', 'three', 'examples', 'textures'), os.path.join(os.path.join(DIST_OUTPUT_DIR, 'node_modules', 'three', 'examples', 'textures')))
    os.makedirs(os.path.join(DIST_OUTPUT_DIR, 'node_modules', 'three.py'))
    shutil.copytree(os.path.join('node_modules', 'three.py', 'js'), os.path.join(DIST_OUTPUT_DIR, 'node_modules', 'three.py', 'js'))
    os.makedirs(os.path.join(DIST_OUTPUT_DIR, 'node_modules', 'stats.js', 'build'))
    shutil.copy(os.path.join('node_modules', 'stats.js', 'build', 'stats.min.js'), os.path.join(DIST_OUTPUT_DIR, 'node_modules', 'stats.js', 'build'))
    os.makedirs(os.path.join(DIST_OUTPUT_DIR, 'node_modules', 'webvr-polyfill', 'build'))
    shutil.copy(os.path.join('node_modules', 'webvr-polyfill', 'build', 'webvr-polyfill.js'), os.path.join(DIST_OUTPUT_DIR, 'node_modules', 'webvr-polyfill', 'build'))



if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--release', help='release (non-debug) mode', action='store_true')
    parser.add_argument('-v', '--verbose', help='enable verbose logging to stdout', action='store_true')
    parser.add_argument('--dist', help='build distributable version', action='store_true')

    args = parser.parse_args()

    if args.verbose:
        logging.basicConfig(level=(logging.DEBUG if app.debug else logging.INFO),
                            format="%(asctime)s %(levelname)s %(name)s %(funcName)s %(lineno)d:  %(message)s")

    app.debug = True
    if args.release:
        app.debug = False

    if args.dist:
        make_dist()
    else:
        main()
