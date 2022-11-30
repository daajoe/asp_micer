#!/usr/bin/env bash

scenario='S3'
lparse_out="exp${scenario}_0gnd_lparse"
mus_out="exp${scenario}_1gnd_MUS"
mis_out="exp${scenario}_2gnd_MIS"

mkdir $lparse_out
mkdir $mus_out
mkdir $mis_out

echo "RUNNING SCENARIO $scenario"

echo "GROUNDING of ASP instances + GENERATING lparse"
for file in $(find transit_graphs/lp -name \*.lp -type f -size -5k) ; do
    echo "$file"
    bfile=$(basename $file)
    #gringo --output=text $file expS1_query.lp 
    gringo --output=smodels $file expS3_vertex_color.lp expS3_query.lp 2> $lparse_out/$bfile.grounder_log | ./lp2normal-2.27 1> $lparse_out/$bfile.lparse
    bzip2 $lparse_out/$bfile.lparse
done


echo "GENERATE REQUIRED INPUT FORMAT(text) from INPUT PROGRAM(lparse) atom(...), body(...), head(...)"
for file in $(find $lparse_out -type f -name \*.lparse.bz2 ) ; do
    bfile=$(basename $file)
    echo $mus_out/$bfile
    bzcat $file | ./lp_parse_choice.py  > $mus_out/$bfile.mus
    bzip2 $mus_out/$bfile.mus
done


echo "GENERATE ground ASP instances"
for file in $(find $mus_out -type f -name \*.mus.bz2) ; do
    bfile=$(basename $file)
    echo $mis_out/$bfile
    echo ".... grounding eic"
    bzcat $file | gringo ./enc1_eic-tight.lp - 2> $mis_out/$bfile.eic.ground_log > $mis_out/$bfile.eic
    echo ".... grounding ric"
    bzcat $file | gringo ./enc1_eic-tight.lp ./enc2_ric_tight.lp - 2> $mis_out/$bfile.ric.ground_log > $mis_out/$bfile.ric
    echo ".... grounding smic"
    bzcat $file | gringo ./enc1_eic-tight.lp ./enc3_smic.lp - 2> $mis_out/$bfile.smic.ground_log > $mis_out/$bfile.smic
    echo ".... compressing"
    bzip2 $mis_out/$bfile.eic $mis_out/$bfile.ric $mis_out/$bfile.smic
done
