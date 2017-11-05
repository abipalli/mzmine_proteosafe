#!/usr/bin/python

import sys
import getopt
import os
import fnmatch
import glob
import xmltodict as xtd



def write_rawinputs(params):
    print "\n---Writing Raw Inputs Module---"
    dict = {}
    dict['@method'] = "net.sf.mzmine.modules.rawdatamethods.rawdataimport.RawDataImportModule"
    dict['parameter'] = {'@name': "Raw data file names"}

    # Parse params dir
    params_dir = params
    params_list = sorted(os.listdir(params_dir))
    for i in range(len(params_list)):
        params_list[i] = os.path.abspath(params_dir + params_list[i])
        print "File "+str(i+1)+": "+params_list[i]

    dict['parameter']['file'] = params_list

    print "---Finished Raw Inputs Module---"

    return dict



def write_massdetect(flowparams, ms_level):
    print "\n---Writing Mass Detection for MS"+str(ms_level)+"---"
    dict = {}
    dict['@method'] = "net.sf.mzmine.modules.rawdatamethods.peakpicking.massdetection.MassDetectionModule"

    parameters = []
    parameters.append({'@name': "Raw data files", '@type': "ALL_FILES"})
    parameters.append({'@name': "Scans", 'ms_level': str(ms_level), 'scan_definition': None})
    parameters.append({'@name': "Mass detector", "@selected": 'Centroid',
        'module': {'@name': "Centroid",
            'parameter': {'@name': "Noise level", '#text': flowparams['massdetect_ms1.noiselevel' if ms_level == 1 else 'massdetect_ms2.noiselevel']}}})
    parameters.append({'@name': "Mass list name", '#text': "masses"})
    parameters.append({'@name': "CDF Filename (optional)", '@selected': "false"})

    print parameters
    print "---Finished Writing Mass Detection for MS"+str(ms_level)+"---"

    dict['parameter'] = parameters
    return dict


def write_chromobuilder(flowparams):
    print "\n---Writing Chromatogram Builder Module---"

    dict = {}
    dict['@method'] = "net.sf.mzmine.modules.masslistmethods.chromatogrambuilder.ChromatogramBuilderModule"

    parameters = []
    parameters.append({'@name': "Raw data files", '@type': "BATCH_LAST_FILES"})
    parameters.append({'@name': "Scans", 'ms_level': '1', 'scan_definition': None})
    parameters.append({'@name': "Mass list", '#text': "masses"})
    parameters.append({'@name': "Min time span (min)", '#text': flowparams['chromobuilder.min_time']})
    parameters.append({'@name': "Min height", '#text': flowparams['chromobuilder.min_height']})
    parameters.append({'@name': "m/z tolerance", 'absolutetolerance': flowparams['chromobuilder.abstolerance'],
        'ppmtolerance': flowparams['chromobuilder.ppmtolerance']})
    parameters.append({'@name': "Suffix", '#text': "chromatograms"})

    print parameters
    print "---Finished Writing Chromatogram Builder Module---"

    dict['parameter'] = parameters
    return dict



def write_deconv(flowparams):
    print "\n---Writing Deconvolution Module---"

    dict = {}
    dict['@method'] = "net.sf.mzmine.modules.peaklistmethods.peakpicking.deconvolution.DeconvolutionModule"

    parameters = []
    parameters.append({'@name': "Peak lists", '@type': "BATCH_LAST_PEAKLISTS"})
    parameters.append({'@name': "Suffix", '#text': "deconvoluted"})
    algorithm = flowparams['deconv.algorithm']
    algo_dict = {'@name': "Algorithm", '@selected': algorithm}
    if algorithm == "Baseline cut-off":
        algo_dict['module'] = {'@name': "Baseline cut-off", 'parameter': [
            {'@name': "Min peak height", '#text': flowparams['deconv.baseline.min_peakheight']},
            {'@name': "Peak duration range (min)", 'max': flowparams['deconv.peak_max'], 'min': flowparams['deconv.peak_min']},
            {'@name': "Baseline level", '#text': flowparams['deconv.baseline.level']}]}
    elif algorithm == "Local minimum search":
        algo_dict['module'] = {'@name': "Local minimum search", 'parameter': [
            {'@name': "Chromatographic threshold", '#text': flowparams['deconv.localmin.threshold']},
            {'@name': "Search minimum in RT range (min)", '#text': flowparams['deconv.localmin.range']},
            {'@name': "Minimum relative height", '#text': flowparams['deconv.localmin.relheight']},
            {'@name': "Minimum absolute height", '#text': flowparams['deconv.localmin.absheight']},
            {'@name': "Min ratio of peak top/edge", '#text': flowparams['deconv.localmin.ratio']},
            {'@name': "Peak duration range (min)", 'min': flowparams['deconv.peak_min'], 'max': flowparams['deconv.peak_max']}]}
    parameters.append(algo_dict)
    ms2mzrange_dict = {'@name': "m/z range for MS2 scan pairing (Da)"}
    if flowparams.has_key('deconv.ms2_mzrange.run'):
        ms2mzrange_dict['@selected'] = "true"
        ms2mzrange_dict['#text'] = flowparams['deconv.ms2_mzrange']
    else:
        ms2mzrange_dict['@selected'] = "false"
    parameters.append(ms2mzrange_dict)
    ms2rtrange_dict = {'@name': "RT range for MS2 scan pairing (min)"}
    if flowparams.has_key('deconv.ms2_rtrange.run'):
        ms2rtrange_dict['@selected'] = "true"
        ms2rtrange_dict['#text'] = flowparams['deconv.ms2_rtrange']
    else:
        ms2rtrange_dict['@selected'] = "false"
    parameters.append(ms2rtrange_dict)
    parameters.append({'@name': "Remove original peak list", '#text': "false"})

    print parameters
    print "---Finished Writing Deconvolution Module---"

    dict['parameter'] = parameters
    return dict


def write_isogroup(flowparams):
    print "\n---Writing Isotope Grouper Module---"

    dict = {}
    dict['@method'] = "net.sf.mzmine.modules.peaklistmethods.isotopes.deisotoper.IsotopeGrouperModule"

    parameters = []
    parameters.append({'@name': "Peak lists", '@type': "BATCH_LAST_PEAKLISTS"})
    parameters.append({'@name': "Name suffix", '#text': "deisotoped"})
    parameters.append({'@name': "m/z tolerance", 'absolutetolerance': flowparams['isogroup.mz_abstolerance'],
        'ppmtolerance': flowparams['isogroup.mz_ppmtolerance']})
    parameters.append({'@name': "Retention time tolerance", '@type': flowparams['isogroup.rettolerance_type'],
        '#text': flowparams['isogroup.rettolerance'] if flowparams['isogroup.rettolerance_type']=='absolute' else str(int(flowparams['isogroup.rettolerance'])/100.)})
    parameters.append({'@name': "Monotonic shape", '#text': "true" if flowparams.has_key('isogroup.monotomicshape') else "false"})
    parameters.append({'@name': "Maximum charge", '#text': flowparams['isogroup.maxcharge']})
    parameters.append({'@name': "Representative isotope", '#text': flowparams['isogroup.repiso']})
    parameters.append({'@name': "Remove original peaklist", '#text': "false"})

    print parameters
    print "---Finished Writing Isotope Grouper Module---"

    dict['parameter'] = parameters
    return dict



def write_orderpeak():
    print "\n---Writing Peak Ordering Module---"

    dict = {}
    dict['@method'] = "net.sf.mzmine.modules.peaklistmethods.orderpeaklists.OrderPeakListsModule"

    parameters = []
    parameters.append({'@name': "Peak lists", '@type': "BATCH_LAST_PEAKLISTS"})

    print parameters
    print "---Finished Writing Peak Ordering Module---"

    dict['parameter'] = parameters
    return dict



def write_joinaligner(flowparams):
    print "\n---Writing Join Aligner Module---"

    dict = {}
    dict['@method'] = "net.sf.mzmine.modules.peaklistmethods.alignment.join.JoinAlignerModule"

    parameters = []
    parameters.append({'@name': "Peak lists", '@type': "BATCH_LAST_PEAKLISTS"})
    parameters.append({'@name': "Peak list name", '#text': "Aligned peak list"})
    parameters.append({'@name': "m/z tolerance", 'absolutetolerance': flowparams['join.mz_abstolerance'],
        'ppmtolerance': flowparams['join.mz_ppmtolerance']})
    parameters.append({'@name': "Weight for m/z", '#text': flowparams['join.mzweight']})
    parameters.append({'@name': "Retention time tolerance", '@type': flowparams['join.rettolerance_type'],
        '#text': flowparams['join.rettolerance'] if flowparams['join.rettolerance_type']=='absolute' else str(int(flowparams['join.rettolerance'])/100.)})
    parameters.append({'@name': "Weight for RT", '#text': flowparams['join.rtweight']})
    parameters.append({'@name': "Require same charge state", '#text': "false"})
    parameters.append({'@name': "Require same ID", '#text': "false"})
    parameters.append({'@name': "Compare isotope pattern", '@selected': "false",
        'parameter':[{'@name': "Minimum absolute intensity"},{'@name': "Minimum score"}]})

    print parameters
    print "---Finished Writing Join Aligner Module---"

    dict['parameter'] = parameters
    return dict



def write_peakfinder(flowparams):
    print "\n---Writing Peak Finder Module---"

    dict = {}
    dict['@method'] = "net.sf.mzmine.modules.peaklistmethods.gapfilling.peakfinder.PeakFinderModule"

    parameters = []
    parameters.append({'@name': "Peak lists", '@type': "BATCH_LAST_PEAKLISTS"})
    parameters.append({'@name': "Name suffix", '#text': "gap-filled"})
    parameters.append({'@name': "Intensity tolerance", '#text': str(int(flowparams['peakfinder.intensitytolerance'])/100.)})
    parameters.append({'@name': "m/z tolerance", 'absolutetolerance': flowparams['peakfinder.mz_abstolerance'],
        'ppmtolerance': flowparams['peakfinder.mz_ppmtolerance']})
    parameters.append({'@name': "Retention time tolerance", '@type': flowparams['peakfinder.rettolerance_type'],
        '#text': flowparams['peakfinder.rettolerance'] if flowparams['peakfinder.rettolerance_type']=='absolute' else str(int(flowparams['peakfinder.rettolerance'])/100.)})
    parameters.append({'@name': "RT correction", '#text': "false"})
    parameters.append({'@name': "Remove original peak list", '#text': "false"})

    print parameters
    print "---Finished Writing Peak Finder Module---"

    dict['parameter'] = parameters
    return dict


def write_rowsfilter(flowparams):
    print "\n---Writing Rows Filter Module---"

    dict = {}
    dict['@method'] = "net.sf.mzmine.modules.peaklistmethods.filtering.rowsfilter.RowsFilterModule"

    parameters = []
    parameters.append({'@name': "Peak lists", '@type': "BATCH_LAST_PEAKLISTS"})
    parameters.append({'@name': "Name suffix", '#text': "filtered_MS2"})
    parameters.append({'@name': "Minimum peaks in a row", '@selected': "true" if flowparams.has_key('rowsfilter.minpeaks_run') else "false",
        '#text': flowparams['rowsfilter.minpeaks']})
    minpeaksisopatt_dict = {'@name': "Minimum peaks in an isotope pattern"}
    if flowparams.has_key("rowsfilter.minpeaksisopatt_run"):
        minpeaksisopatt_dict['@selected'] = "true"
        minpeaksisopatt_dict['#text'] = flowparams['rowsfilter.minpeaksisopatt']
    else:
        minpeaksisopatt_dict['@selected'] = "false"
    parameters.append(minpeaksisopatt_dict)
    parameters.append({'@name': "m/z", '@selected': "false"})
    rettime_dict = {'@name': "Retention time"}
    if flowparams.has_key('rowsfilter.rettime_run'):
        rettime_dict['@selected'] = "true"
        rettime_dict['min'] = flowparams['rowsfilter.rettime_min']
        rettime_dict['max'] = flowparams['rowsfilter.rettime_max']
    else:
        rettime_dict['@selected'] = "false"
    durtime_dict = {'@name': "Peak duration range"}
    if flowparams.has_key('rowsfilter.durtime_run'):
        durtime_dict['@selected'] = "true"
        durtime_dict['min'] = flowparams['rowsfilter.durtime_min']
        durtime_dict['max'] = flowparams['rowsfilter.durtime_max']
    else:
        durtime_dict['@selected'] = "false"
    parameters.append(durtime_dict)
    parameters.append({'@name': "Parameter", '#text': "No parameters defined"})
    parameters.append({'@name': "Only identified?", '#text': "false"})
    parameters.append({'@name': "Text in identity", '@selected': "false"})
    parameters.append({'@name': "Text in comment", '@selected': "false"})
    parameters.append({'@name': "Keep or remove rows", '#text': "Keep rows that match all criteria"})
    parameters.append({'@name': "Keep only peaks with MS2 scan (GNPS)", '#text': "true"})
    parameters.append({'@name': "Reset the peak number ID", '#text': "true" if flowparams.has_key('rowsfilter.resetpeaknum') else "false"})
    parameters.append({'@name': "Remove source peak list after filtering", '#text': "false"})

    print parameters
    print    "---Finished Writing Rows Filter Module---"

    dict['parameter'] = parameters
    return dict



def write_csvexport(filename):
    print "\n---Writing CSV Export Module---"

    dict = {}
    dict['@method'] = "net.sf.mzmine.modules.peaklistmethods.io.csvexport.CSVExportModule"

    parameters = []
    parameters.append({'@name': "Peak lists", '@type': "BATCH_LAST_PEAKLISTS"})
    parameters.append({'@name': "Filename", '#text': filename})
    parameters.append({'@name': "Field separator", '#text': ","})
    parameters.append({'@name': "Export common elements",
            'item': [{'#text': "Export row ID"},{'#text': "Export row m/z"},{'#text': "Export row retention time"},{'#text': "Export row number of detected peaks"}]})
    parameters.append({'@name': "Export data file elements", 'item': [{'#text': "Peak status"}, {'#text':"Peak m/z"}, {'#text': "Peak RT"}, {'#text': "Peak area"},
            {'#text': "Peak charge"}]})
    parameters.append({'@name': "Export all IDs for peak", '#text': "false"})
    parameters.append({'@name': "Export quantitation results and other information", '#text': "false"})
    parameters.append({'@name': "Identification separator", '#text': ";"})


    print parameters
    print "---Finished Writing CSV Export Module---"

    dict['parameter'] = parameters
    return dict



def write_gnpsexport(filename):
    print "\n---Writing GNPS Export Module---"

    dict = {}
    dict['@method'] = "net.sf.mzmine.modules.peaklistmethods.io.gnpsexport.GNPSExportModule"

    parameters = []
    parameters.append({'@name': "Peak lists", '@type': "BATCH_LAST_PEAKLISTS"})
    parameters.append({'@name': "Filename", '#text': filename})
    parameters.append({'@name': "Mass list", '#text': "masses"})

    print parameters
    print "---Finished Writing GNPS Export Module---"

    dict['parameter'] = parameters
    return dict



def write_peakgroup(flowparams):
    print '\n---Writing Peak Grouping Module'

    dict = {}
    dict['@method'] = "net.sf.mzmine.modules.peaklistmethods.coelution.PeakGroupingModule"

    parameters = []
    parameters.append({'@name':"Name suffix", '#text':"decoeluted"})
    parameters.append({'@name':"Peak lists", '@type':"BATCH_LAST_PEAKLISTS"})
    parameters.append({'@name':"Mass list", '#text':"masses"})
    parameters.append({'@name':"deisotope", '#text':"true"})
    parameters.append({'@name':"remove features without isotope pattern", '#text':"true" if flowparams.has_key('peakgroup.isopattern_only') else "false"})
    parameters.append({'@name':"minimal intensity for interval selection", '#text':str(float(flowparams['peakgroup.min_interval'])/100.)})
    parameters.append({'@name':"minimal intensity overlap", '#text':str(float(flowparams['peakgroup.min_overlap'])/100.)})
    parameters.append({'@name':"minimal correlation", '#text':str(float(flowparams['peakgroup.min_corr'])/100.)})

    print parameters
    print "--Finished Writing Peak Grouping Module---"

    dict['parameter'] = parameters
    return dict



def write_siriusexport(filename):
    print "\n---Writing Sirius Export Module---"

    dict = {}
    dict['@method'] = "net.sf.mzmine.modules.peaklistmethods.io.siriusexport.SiriusExportModule"

    parameters = []
    parameters.append({'@name': "Peak lists", '@type': "BATCH_LAST_PEAKLISTS"})
    parameters.append({'@name': "Filename", '#text': filename})
    #parameters.append({'@name': "Merging Mode", '#text': "Maximum"}) # version 2.28
    parameters.append({'@name':"include MS1", '#text':"true"})  # version 2.29
    parameters.append({'@name': "Mass list", '#text': "masses"})

    print parameters
    print "---Finished Writing Sirius Export Module---"

    dict['parameter'] = parameters
    return dict



def write_steps(flowparams, params, output):
    xml = {'batch':{}}

    # Write batchsteps
    batchsteps = []

    batchsteps.append(write_rawinputs(params))

    if flowparams.has_key('massdetect_ms1.run'):
        batchsteps.append(write_massdetect(flowparams, 1))
    if flowparams.has_key('massdetect_ms2.run'):
        batchsteps.append(write_massdetect(flowparams, 2))
    if flowparams.has_key('chromobuilder.run'):
        batchsteps.append(write_chromobuilder(flowparams))
    if flowparams.has_key('deconv.run'):
        batchsteps.append(write_deconv(flowparams))
    if flowparams.has_key('peakgroup.run'):
        batchsteps.append(write_peakgroup(flowparams))
    if flowparams.has_key('join.run'):
        batchsteps.append(write_joinaligner(flowparams))
    if flowparams.has_key('peakfinder.run'):
        batchsteps.append(write_peakfinder(flowparams))
    batchsteps.append(write_csvexport("feature_table_all.csv"))
    if flowparams.has_key('rowsfilter.run'):
        batchsteps.append(write_rowsfilter(flowparams))
    batchsteps.append(write_csvexport("feature_table_MS2.csv"))
    batchsteps.append(write_gnpsexport("spectral_data_MS2.mgf"))
    batchsteps.append(write_siriusexport("spectral_data_MS1_MS2.mgf"))

    # Update xml with all batchsteps
    xml['batch']['batchstep'] = batchsteps

    with open(output, 'w') as o:
        o.write(xtd.unparse(xml, pretty=True))



def convert_flowparams_to_dict(flowparams):
    dict = {}

    for param in flowparams:
        dict[param['@name']] = param['#text']

    return dict



def main():
    if len(sys.argv) < 3:
        exit()

    # Collect arguments
    with open(sys.argv[1]) as f:
        flowparams = convert_flowparams_to_dict(xtd.parse(f.read())['parameters']['parameter'])
    params = sys.argv[2] + '/'
    batch = "batch/batch.xml"

    # Print args
    print("flowparams: "+str(flowparams))
    print("params: "+params)
    print("batch: "+batch)

    # Write Steps
    write_steps(flowparams, params, batch)



if __name__ == '__main__':
    main()
