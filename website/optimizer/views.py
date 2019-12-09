from django.shortcuts import render
from django.http import HttpResponseRedirect, HttpResponse
from .Optimizer import get_daily_roster, create_predictions
from .forms import OptimizerForm, SlateForm
from django.contrib import messages
from django.core.files.storage import FileSystemStorage
from django.http import FileResponse
import os
from pydfs_lineup_optimizer import get_optimizer, Site, Sport, CSVLineupExporter
import pandas as pd
from pathlib import Path


def get_slates():
    slate_files = os.listdir(Path(r'/home/ubuntu/Fantasy-Fire/website/optimizer/Slates'))
    slates = []
    for slate in slate_files:
        if "Main" in slate:
            slates.insert(0, slate[:-4])
        elif "Night" in slate:
            slates.insert(2, slate[:-4])
        elif "Turbo" in slate:
            slates.insert(1, slate[:-4])
        else:
            slates.append(slate[:-4])
    return slates


# Create your views here.
def home(request):
    return render(request, 'optimizer/home.html', {})


def about(request):
    return render(request, 'optimizer/about.html', {})


def create_optimizer(request):
    if request.method == 'POST':
        form = OptimizerForm(request.POST)
        form2 = SlateForm(request.POST)
        if form2.is_valid() and 'change_slate' in request.POST:
            slate = form2.cleaned_data['slate']
            form = OptimizerForm()
            form2 = SlateForm(initial={'slate': slate})
            df = get_daily_roster(Path('//home/ubuntu/Fantasy-Fire/website/optimizer/prediction.csv'))
            # df = create_predictions(df)
            df = create_predictions(df,
                                    slate=Path('//home/ubuntu/Fantasy-Fire/website/optimizer/Slates/' + slate + '.csv'))
            df['Min Exposure'] = 0
            df['Max Exposure'] = 1
            df['Value'] = round(df['Predicted_FP'] / (df['Salary'] / 1000),2)
            df.insert(0, "Include", '', True)
            for ind in df.index:
                df['Predicted_FP'][ind] = "<input type='number' form='optimizer' name='fantasy_points_" + str(
                    ind) + "' value=" + str(round(df['Predicted_FP'][ind], 2)) + " id='id_predicted_fp'>"
                # df['Predicted FP'] = df['Predicted FP'].apply(lambda x: round(float(x), 2))
                # df['Predicted FP'] = df['Predicted FP'].apply(
                #     lambda x: "<input type='text' form='optimizer' name='fantasy_points_" + df['Name'] + "' value=" + str(
                #         x) + " id='id_predicted_fp'>")
                df['Min Exposure'][ind] = "<input type='text' name='min_exposure_" + str(ind) + "' value=" + str(
                    0) + ">"
                df['Max Exposure'][ind] = "<input type='text' name='max_exposure_" + str(ind) + "' value=" + str(
                    1) + ">"
                df['Include'][ind] = "<input type='checkbox' id='child' name='include_" + str(ind) + "' checked>"
            df.rename(columns={
                'Include': "<input type='checkbox' id='parent' onclick='checkAll()' checked>"},
                inplace=True)
            html_table = df.to_html(index=False, justify='left', escape=False, table_id='slateData',
                                    classes=[
                                        'table sorted table-bordered table-striped table-hover table-responsive table-sm container-fluid'])
            return render(request, 'optimizer/optimizer.html',
                          {'form': form, 'player_table': html_table, 'form2': form2, 'slate': slate})
        if form.is_valid():
            slate = form2.cleaned_data['slate']
            min_salary = form.cleaned_data['min_salary']
            max_exposure = form.cleaned_data['max_exposure']
            no_lineups = form.cleaned_data['no_lineups']
            deviation = form.cleaned_data['deviation']
            generation_type = form.cleaned_data['generation_type']

            if "Showdown" in slate:
                optimizer = get_optimizer(Site.DRAFTKINGS_CAPTAIN_MODE, Sport.BASKETBALL)
            else:
                optimizer = get_optimizer(Site.DRAFTKINGS, Sport.BASKETBALL)

            df = pd.read_csv(Path("//home/ubuntu/Fantasy-Fire/website/optimizer/Slates/" + slate + ".csv"))
            df2 = pd.read_csv(Path(r"//home/ubuntu/Fantasy-Fire/website/optimizer/prediction.csv"))
            result = df.merge(df2, left_on='Name', right_on='name', how='left')
            # result = result.drop(
            #     columns=['AvgPointsPerGame'])
            result = result.fillna(0)
            includes = []
            fantasy_points = []
            min_exposures = []
            max_exposures = []
            deviations = []
            for key, value in request.POST.items():
                if 'include' in key:
                    includes.append(key)
                elif 'fantasy_points' in key:
                    fantasy_points.append(value)
                elif 'min_exposure' in key:
                    min_exposures.append(value)
                elif 'max_exposure' in key:
                    max_exposures.append(value)
                elif 'deviation' in key:
                    deviations.append(value)
            result['Min Exposure'] = 0
            result['Max Exposure'] = 1
            for ind in result.index:
                result['AvgPointsPerGame'][ind] = fantasy_points[ind]
                if int(max_exposure) != int(max_exposures[ind]) and int(max_exposures[ind]) > 1:
                    result['Max Exposure'][ind] = int(max_exposures[ind]) / 100
                result['Min Exposure'][ind] = int(min_exposures[ind]) / 100
            # result = result.rename(columns={'max_exposure': 'Max Exposure', 'min_exposure': 'Min Exposure'})
            result.to_csv(Path("//home/ubuntu/Fantasy-Fire/website/optimizer/Predictions.csv"))
            optimizer.load_players_from_csv(
                Path('//home/ubuntu/Fantasy-Fire/website/optimizer/Predictions.csv'))
            optimizer.set_deviation(0, int(deviation) / 100)
            optimizer.set_min_salary_cap(min_salary)
            for player in optimizer.players:
                id = player.id
                playa = optimizer.get_player_by_id(id)
                optimizer.remove_player(playa)
            for i in includes:
                id = str(result['ID'][int(i[i.find('_') + 1:])])
                player = optimizer.get_player_by_id(id)
                optimizer.restore_player(player)
            exporter = CSVLineupExporter(
                optimizer.optimize(no_lineups, randomness=generation_type, max_exposure=max_exposure/100))
            exporter.export(Path('//home/ubuntu/Fantasy-Fire/website/optimizer/lineups.csv'))

            with open('//home/ubuntu/Fantasy-Fire/website/optimizer/lineups.csv') as myfile:
                response = HttpResponse(myfile, content_type='text/csv')
                response['Content-Disposition'] = 'attachment; filename=lineups.csv'
                return response

    else:
        form = OptimizerForm()
        form2 = SlateForm(initial={'slate': 'Main_Slate'})
        df = get_daily_roster(Path('//home/ubuntu/Fantasy-Fire/website/optimizer/prediction.csv'))
        # df = create_predictions(df)
        df = create_predictions(df,
                                slate=Path('//home/ubuntu/Fantasy-Fire/website/optimizer/Slates/Main_Slate.csv'))
        df['Min Exposure'] = 0
        df['Max Exposure'] = 1
        df['Value'] = round(df['Predicted_FP'] / (df['Salary'] / 1000),2)
        df.insert(0, "Include", '', True)
        for ind in df.index:
            df['Predicted_FP'][ind] = "<input type='number' form='optimizer' name='fantasy_points_" + str(
                ind) + "' value=" + str(round(df['Predicted_FP'][ind], 2)) + " id='id_predicted_fp'>"
            # df['Predicted FP'] = df['Predicted FP'].apply(lambda x: round(float(x), 2))
            # df['Predicted FP'] = df['Predicted FP'].apply(
            #     lambda x: "<input type='text' form='optimizer' name='fantasy_points_" + df['Name'] + "' value=" + str(
            #         x) + " id='id_predicted_fp'>")
            df['Min Exposure'][ind] = "<input type='text' name='min_exposure_" + str(ind) + "' value=" + str(
                0) + ">"
            df['Max Exposure'][ind] = "<input type='text' name='max_exposure_" + str(ind) + "' value=" + str(
                1) + ">"
            df['Include'][ind] = "<input type='checkbox' id='child' name='include_" + str(ind) + "' checked>"
        df.rename(columns={
            'Include': "<input type='checkbox' id='parent' onclick='checkAll()' checked>"},
            inplace=True)
        # df['Value'] = df['Predicted_FP'] / (df['Salary'] / 1000)
        # html_table = df.to_html(index=False, justify='left', escape=False, table_id='slateData',
        #                         classes=[
        #                             'table sorted table-bordered table-striped table-hover table-responsive table-sm searchable container-fluid'])
        html_table = df.to_html(index=False, justify='left', escape=False, table_id='slateData',
                                classes=[
                                    'sorted'])
        return render(request, 'optimizer/optimizer.html',
                      {'form': form, 'player_table': html_table, 'form2': form2, 'slate': 'Main_Slate'})
