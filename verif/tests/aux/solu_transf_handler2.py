solu= feProblem.getSoluProc
solCtrl= solu.getSoluControl
solModels= solCtrl.getModelWrapperContainer
sm= solModels.newModelWrapper("sm")
cHandler= sm.newConstraintHandler("transformation_constraint_handler")

numberer= sm.newNumberer("default_numberer")
numberer.useAlgorithm("rcm")
analysisAggregations= solCtrl.getAnalysisAggregationContainer
analysisAggregation= analysisAggregations.newAnalysisAggregation("analysisAggregation","sm")

solAlgo= analysisAggregation.newSolutionAlgorithm("linear_soln_algo")
integ= analysisAggregation.newIntegrator("load_control_integrator",xc.Vector([]))
soe= analysisAggregation.newSystemOfEqn("band_spd_lin_soe")
solver= soe.newSolver("band_spd_lin_lapack_solver")

analysis= solu.newAnalysis("static_analysis","analysisAggregation","")
result= analysis.analyze(1)
