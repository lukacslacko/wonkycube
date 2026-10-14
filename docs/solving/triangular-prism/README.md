# Triangular-prism solution guide

[Read the nine-page illustrated PDF](../triangular-prism-solving-guide.pdf).

This is a full shape solution for the [64 mm non-wavy triangular prism](../../../designs/triangular-prism-v1/README.md): vertical petals, screwed-center orientations, horizontal petals, then floating corners. It includes all 40 three-cycle setup rows, inverse algorithms, examples and troubleshooting. Follow its fixed axis names: R = C02, L = C01, B = C03, U = C04, D = C05. Earlier informal axis names need not match this convention.

`verify.py` generates `algorithms.json` and checks the complete method on all 96 side-center/vertical-petal states, all 360 permutations of each final family, and 1,000 random 80-move scrambles. Each of the 40 setup rows is independently checked with the actual CAD axes and 3D orientation matrices. `move_model.py` is the exact oriented D3 action. These are mathematical move checks, not new print tests.

From the repository root, with the triangular-prism CAD requirements installed:

```sh
python docs/solving/triangular-prism/verify.py
```

`render.py` regenerates the figures from the published STL meshes. `build_pdf.py` uses ReportLab and pypdf to regenerate the PDF from the committed figures and algorithm data. The render/build scripts use the macOS Arial fonts at their normal system location; the PDF itself works on any PDF reader. `pdf-validation.json` records the delivered PDF hash and review, and `layout-checks.json` records paragraph bounds. Install `reportlab` and `pypdf` in addition to the CAD requirements if rebuilding the document. All original guide content, source and figures are MIT licensed with this repository.
