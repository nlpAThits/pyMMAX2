from pymmax2.pyMMAX2 import *
import jpype, sys, argparse
from glob import glob

parser = argparse.ArgumentParser()
action = parser.add_mutually_exclusive_group(required=True)
# For loading a single file
action.add_argument('--mmax_file', default = None)
# For loading all .mmax files in mmax_dir
action.add_argument('--mmax_dir', default = None)
parser.add_argument('--common_paths', required = False,  default = "")
# Provide path to Libs folder in MMAX2 installation (required for JPype integration)
parser.add_argument('--mmax2_libs',  required = False, default = None)
args=parser.parse_args()

MMAX2_CLASSPATH	= ""
if args.mmax2_libs:
	for f in [f for f in glob(args.mmax2_libs+'**', recursive=True) if f.endswith(".jar")]:
		MMAX2_CLASSPATH+=f+":"	# use ; instead of : for Windows
	jpype.startJVM(jpype.getDefaultJVMPath(), "-Djava.class.path="+MMAX2_CLASSPATH)

if args.mmax_dir:
	files = [f for f in glob(args.mmax_dir+'**', recursive=True) if f.endswith(".mmax")]
else:
	files = [args.mmax_file]

for f in files:
	pd = MMAX2Discourse(f, common_paths=args.common_paths, mmax2_java_binding=jpype if jpype.isJVMStarted() else None)
	try:
		pd.load_markables(verbose=False)
	except MultipleInvalidMMAX2AttributeExceptions as mive:
		print('%s validation exceptions, e.g.\n%s'%(str(mive.get_exception_count()),
			                             str(mive.get_exception_at(0)).strip()))
	pd.info()

	# Get dict of all coref sets in current discourse
	coref_sets = pd.get_markablelevel_by_name("coref").get_markablesets(set_att="coref_class")
	pvg = Network(height='100%', width='100%', layout=False)
#	pvg.force_atlas_2based(overlap=1, damping=1, spring_length=200, central_gravity=0.0005)
	# Go over all coref set ids
	for set_id in coref_sets:
		coref_sets[set_id].to_discourse_order()
		for m in coref_sets[set_id].get_markables():
			pvg.add_node(m.get_id(), mass=5, shape='box', borderWidth=3, shadow=True, font="8 courier black bold", label=m.render_string()[0], pos=m.get_discourse_position())
#			print(pvg.nodes)
			if len(pvg.node_ids)>1:
				a_id=pvg.node_ids[-1]
				b_id=pvg.node_ids[-2]
				pvg.add_edge(a_id,b_id, weight=pvg.nodes[-1]['pos']-pvg.nodes[-2]['pos'], label=str(pvg.nodes[-1]['pos']-pvg.nodes[-2]['pos']))
	pvg.toggle_physics(True)
	pvg.show_buttons()
	pvg.save_graph("test.html")
