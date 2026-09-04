Image processing
================

``grainMeaning``
----------------

**Type:** integer. **Accepted values:** ``0`` for light grains or ``1`` for dark
grains. **Required:** yes.

``threshold``
-------------

**Type:** number. **Accepted values:** 0 through 1, inclusive. The image is read
in grayscale and converted into a binary grain and pore-space mask.

``rescale``
-----------

**Type:** positive number. Rescales the input image before contour extraction.
Values below 1 reduce the number of pixels. See
`skimage.transform.rescale <https://scikit-image.org/docs/stable/api/skimage.transform.html#skimage.transform.rescale>`_.

``grainsSize``
--------------

**Type:** nonnegative integer. **Units:** pixels. Removes connected grain
objects at or below the configured size. See
`remove_small_objects <https://scikit-image.org/docs/stable/api/skimage.morphology.html#skimage.morphology.remove_small_objects>`_.

.. _border-grains-tol:

``borderTol`` and ``grainsTol``
-------------------------------

**Type:** nonnegative number. Polygon-approximation tolerances for the external
border and interior grains. Larger values reduce the number of contour points.
See `approximate_polygon <https://scikit-image.org/docs/stable/auto_examples/edges/plot_polygon.html>`_.

.. figure:: ../figs/size_500_5_5.png
   :alt: Contours generated with grain size 500 and tolerances 5

.. figure:: ../figs/size_100_1_1.png
   :alt: Contours generated with grain size 100 and tolerances 1

.. figure:: ../figs/size_0_0_0.png
   :alt: Contours generated without grain removal or polygon simplification

   Extracted contours for ``grainsSize``, ``borderTol``, and ``grainsTol`` of
   500, 5, 5; 100, 1, 1; and 0, 0, 0, respectively.

.. tip::

   Smaller size and tolerance values retain more geometric detail, but increase
   mesh-generation and simulation time.
