PREREQUISITES
=============
- add LFC_HOME and LFC_HOST to your environment,
   e.g. add to you .bashrc something like:
   export LFC_HOME='/grid/lsgrid/marc/'
   export LFC_HOST=lfc.grid.sara.nl

- startGridSession lsgrid

INSTALL
=======

1) install 'cluster_manager' using Enhance (see github.com/mhulsman).

CHANGE environment
==================
after installation, or moving scripts into work directory, if grid is used:
1) use <enhance_dir>/upload to upload environment

RUN just python
===============
1) adapt load_env_worker.sh
2) if you need extra files, put them in the work directory (<enhance_dir>/sys_enhance/work)
   and update environment (last paragraph)
3) if you use ipengine_loadenv.jdl, change XXNJOBXX to the number of jobs you want to run
4) glite-wms-job-submit -d <delegation_id> -o <jobid_file>  ipengine_loadenv.jdl


RUN ipython parallel
====================
0) First, make sure ports are open on <hostname of ui> that were given during install.

Then, go to your python directory from which you run your project:
1) cd <your_project>
2) <environment_dir>/cluster.py
   - start controllers and engines from interface
3) ipython
   - start tasks
   e.g.:
   from IPython.kernel import client
   
   #METHOD 1
   mec = client.MultiEngineClient()
   mec['b'] = 2  #sets b in all clients
   mec.execute("a = b * 2")
   print mec['a']  #prints for each client: 4
   
   #METHOD 2
   tc = client.TaskClient()
   strtask = """a = b * 2"""
   b = 1 
   task = client.StringTask(strtask, ('a',), {'b':2})
   task_id = tc.run(task)
   tres = tc.get_task_result(task_id,block=True)
   print tres['a']  #prints 2


CLUSTER STORAGE
===============
For sending large files to/from engines, make use of submit / receive functions in cluster_storage.py:

#somewhere on grid, do:
id = submit(your_object)
#or, with fixed id:
id = submit(your_object,"your_id")

#somewhere else on grid, do:
object = receive(id)    

#clean up
destroy(id)

