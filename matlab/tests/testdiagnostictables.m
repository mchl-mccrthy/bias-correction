function tests = testdiagnostictables
tests = functiontests(localfunctions);
end

function testCoincidentMeans(testCase)
station = array2table([1 NaN; NaN NaN; 3 NaN]);
raw = array2table([2 10; 100 10; NaN 10]);
bc = array2table([1.5 10; 100 10; 5 10]);
[obs_mean,raw_mean,bc_mean] = getstationmeans(station,raw,bc);
verifyEqual(testCase,obs_mean,[1 NaN]);
verifyEqual(testCase,raw_mean,[2 NaN]);
verifyEqual(testCase,bc_mean,[1.5 NaN]);
end

function testOverviewMeansAndTrends(testCase)
summary = makesummarytable('tas',[1 3],[-1 5],[1 3],...
    [2 4],[0 0],[3 5],[0 0],[10 20],[12 24],[10 20]);
verifyEqual(testCase,summary.Observed_mean,[15;15]);
verifyEqual(testCase,summary.Model_mean,[18;15]);
verifyEqual(testCase,summary.Observed_linear_trend,[2;2]);
verifyEqual(testCase,summary.Model_linear_trend,[2;2]);
verifyEqual(testCase,summary.MAE_linear_trends,[2;0]);
end

function testDiagnosticCsvFiles(testCase)
folder = tempname;
mkdir(folder)
cleanup = onCleanup(@() rmdir(folder,'s')); %#ok<NASGU>
time = (datetime(2000,1,1):datetime(2002,12,31))';
values = year(time)-1999;
cfg.clim_var_name = 'tas';
cfg.clim_var_units = 'degC';
cfg.agg_method = 'mean';
cfg.file_path_raw_data = fullfile(folder,'raw.nc');
cfg.file_path_bc_data = fullfile(folder,'bc.nc');
cfg.file_path_station_coords = fullfile(folder,'coords.csv');
cfg.file_path_station_clim_var = fullfile(folder,'stations.csv');
cfg.file_path_figures_tables = folder;
writetable(table({'ALT';'SMA'},[8;9],[46;46],...
    'VariableNames',{'station','lon','lat'}),cfg.file_path_station_coords)
writetable(table(year(time),month(time),day(time),values,values,...
    'VariableNames',{'year','month','day','ALT','SMA'}),cfg.file_path_station_clim_var)
files = {cfg.file_path_raw_data,cfg.file_path_bc_data};
for k = 1:2
    file = files{k};
    nccreate(file,'lon','Dimensions',{'lon',2});
    ncwrite(file,'lon',[8;9]);
    nccreate(file,'lat','Dimensions',{'lat',2});
    ncwrite(file,'lat',[46;47]);
    nccreate(file,'time','Dimensions',{'time',numel(time)});
    ncwrite(file,'time',(0:numel(time)-1)');
    ncwriteatt(file,'time','units','days since 2000-01-01');
    nccreate(file,'tas','Dimensions',{'lon',2,'lat',2,'time',numel(time)});
    grid = repmat(reshape(values+3-k,1,1,[]),2,2,1);
    grid(:,2,:) = grid(:,2,:) + repmat(reshape(20*values,1,1,[]),2,1,1);
    ncwrite(file,'tas',grid);
end
diagnostics = makediagnostics(cfg);
overview = readtable(fullfile(folder,'overview','tas_diagnostics_summary.csv'),'VariableNamingRule','preserve');
verifyEqual(testCase,overview{:,6},[24;23],'AbsTol',1e-10);
verifyEqual(testCase,overview{:,7},[11;11],'AbsTol',1e-10);
verifyEqual(testCase,overview{:,6},diagnostics.summary_table.Domain_mean_yearly,'AbsTol',1e-10);
verifyFalse(testCase,any(contains(overview.Properties.VariableNames,'Observed')));
for name = {'ALT','SMA'}
    station = readtable(fullfile(folder,'individual_stations',...
        [name{1} '_tas_diagnostics_summary.csv']),'VariableNamingRule','preserve');
    verifyEqual(testCase,station.Dataset,{'Raw';'Bias-corrected'});
    verifyEqual(testCase,station.Station,repmat(name,2,1));
    verifyTrue(testCase,ismember(['AE linear trend (' char(176) 'C year^-1)'],station.Properties.VariableNames));
    verifyEqual(testCase,station{:,10},[1;1],'AbsTol',1e-10);
end
cfg.agg_method = 'sum';
cfg.clim_var_units = 'mm day^{-1}';
diagnostics = makediagnostics(cfg);
overview = readtable(fullfile(folder,'overview','tas_diagnostics_summary.csv'),'VariableNamingRule','preserve');
verifyTrue(testCase,ismember('Domain mean yearly (mm year^-1)',overview.Properties.VariableNames));
verifyTrue(testCase,ismember('Domain linear trend (mm year^-2)',overview.Properties.VariableNames));
station = readtable(fullfile(folder,'individual_stations','ALT_tas_diagnostics_summary.csv'),...
    'VariableNamingRule','preserve');
verifyTrue(testCase,ismember('MAE quantiles (mm day^-1)',station.Properties.VariableNames));
verifyEqual(testCase,station.('Observed mean yearly (mm year^-1)'),repmat(mean([366 730 1095]),2,1),'AbsTol',1e-10);
verifyEqual(testCase,overview{:,6},[mean(11*[366 730 1095]+2*[366 365 365]);...
    mean(11*[366 730 1095]+[366 365 365])],'AbsTol',1e-10);
end
